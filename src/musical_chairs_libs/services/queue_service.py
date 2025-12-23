#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
#import musical_chairs_libs.dtos_and_utilities.logging as logging
from typing import (
	Any,
	Callable,
	Optional,
	Iterator,
	cast,
	Collection,
	Sequence,
	Set,
	Tuple,
	Iterable
)
from sqlalchemy import (
	select,
	desc,
	func,
	insert,
	update,
	literal,
	union_all,
	true,
	String
)
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.sql.functions import coalesce
from .station_service import StationService
from .accounts_service import AccountsService
from .song_info_service import SongInfoService
from .path_rule_service import PathRuleService
from .template_service import TemplateService
from .user_actions_history_service import UserActionsHistoryService
from musical_chairs_libs.tables import (
	songs,
	stations,
	stations_songs as stations_songs_tbl, stsg_stationFk, stsg_songFk,
	user_action_history as user_action_history_tbl, uah_pk, uah_queuedTimestamp,
	uah_timestamp, uah_action,
	station_queue, q_userActionHistoryFk, q_songFk, q_stationFk,
	albums,
	artists,
	song_artist,
	sgar_pk, sgar_songFk, sgar_artistFk, sgar_isPrimaryArtist,
	sg_pk, sg_name, sg_path, sg_albumFk, sg_internalpath, sg_deletedTimstamp,
	sg_track,
	stations as stations_tbl, st_pk, st_typeid,
	ar_pk, ar_name,
	ab_pk, ab_name,
	last_played, lp_songFk, lp_stationFk, lp_timestamp,
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	CatalogueItem,
	CurrentPlayingInfo,
	get_datetime,
	QueuedItem,
	SongListDisplayItem,
	StationInfo,
	UserRoleDef,
	LastPlayedItem,
	TrackingInfo
)
from musical_chairs_libs.file_reference import SqlScripts
from musical_chairs_libs.protocols import SongPopper, RadioPusher
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationRequestTypes,
	StationTypes
)
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)




def choice(
	items: Sequence[Any],
	sampleSize: int
) -> Collection[Any]:
	aSize = len(items)
	pSize = len(items) + 1
	# the sum of weights needs to equal 1
	weights = [2 * (float(n) / (pSize * aSize)) for n in range(1, pSize)]
	return numpy_choice(items, sampleSize, p = cast(Any,weights), replace=False).tolist()

class QueueService(SongPopper, RadioPusher):

	def __init__(
		self,
		conn: Optional[Connection]=None,
		stationService: Optional[StationService]=None,
		accountService: Optional[AccountsService]=None,
		songInfoService: Optional[SongInfoService]=None,
		choiceSelector: Optional[
			Callable[[Sequence[Any], int], Collection[Any]]
		]=None,
		pathRuleService: Optional[PathRuleService]=None,
		userActionsHistoryService: Optional[UserActionsHistoryService]=None,
	) -> None:
			if not conn:
				raise RuntimeError("No connection provided")
			if not stationService:
				stationService = StationService(conn)
			if not accountService:
				accountService = AccountsService(conn)
			if not songInfoService:
				songInfoService = SongInfoService(conn)
			if not choiceSelector:
				choiceSelector = choice
			if not pathRuleService:
				pathRuleService = PathRuleService(conn)
			if not userActionsHistoryService:
				userActionsHistoryService = UserActionsHistoryService(conn)
			self.conn = conn
			self.station_service = stationService
			self.account_service = accountService
			self.song_info_service = songInfoService
			self.choice = choiceSelector
			self.get_datetime = get_datetime
			self.path_rule_service = pathRuleService
			self.user_actions_history_service = userActionsHistoryService
			self.queue_size = 50
			self.album_queue_size = 3

	def get_all_station_possibilities(
		self, stationPk: int
	) -> Sequence[RowMapping]:
		query = select(sg_pk, sg_path) \
			.select_from(stations) \
			.join(stations_songs_tbl, st_pk == stsg_stationFk) \
			.join(songs, sg_pk == stsg_songFk) \
			.join(station_queue, (q_stationFk == st_pk) \
				& (q_songFk == sg_pk), isouter=True) \
			.join(last_played, (lp_stationFk == st_pk) \
				& (lp_songFk == sg_pk), isouter=True
			)\
			.join(user_action_history_tbl,
				(uah_pk == q_userActionHistoryFk) & uah_timestamp.isnot(None),
				isouter=True
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationPk) \
			.group_by(sg_pk, sg_path) \
			.order_by(
				func.max(uah_queuedTimestamp),
				func.max(uah_timestamp),
				lp_timestamp,
				func.rand()
			)

		rows = self.conn.execute(query).mappings().fetchall()
		return rows


	def get_random_songIds(
		self,
		stationId: int,
		deficitSize: int
	) -> Collection[int]:
		rows = self.get_all_station_possibilities(stationId)
		sampleSize = deficitSize if deficitSize < len(rows) else len(rows)
		songIds = [r[sg_pk] for r in rows]
		if not songIds:
			raise RuntimeError("No song possibilities were found")
		selection = self.choice(songIds, sampleSize)
		return selection


	def queue_insert_songs(
		self,
		songIds: Collection[int],
		stationId: int,
		userId: Optional[int]=None,
		trackingInfo: Optional[TrackingInfo]=None
	):
		userAgentId = self.user_actions_history_service\
			.add_user_agent(trackingInfo.userAgent) if trackingInfo else None
		timestamp = self.get_datetime().timestamp()
		insertedIds: list[int] = []
		timestampOffset = 0.0
		for _ in songIds:
			historyInsert = insert(user_action_history_tbl)
			insertedId = self.conn.execute(historyInsert, {
					"queuedtimestamp": timestamp + timestampOffset,
					"action": UserRoleDef.STATION_REQUEST.value,
					"userfk": userId,
					"ipv4address": trackingInfo.ipv4Address if trackingInfo else None,
					"ipv6address": trackingInfo.ipv6Address if trackingInfo else None,
					"useragentsfk": userAgentId

				}).inserted_primary_key
			timestampOffset += .1
			if insertedId:
				insertedIds.append(cast(int,insertedId[0]))
		params = [{
			"stationfk": stationId,
			"songfk": s[0],
			"useractionhistoryfk": s[1]
		} for s in zip(songIds,insertedIds)]
		queueInsert = insert(station_queue)
		self.conn.execute(queueInsert, params)


	def fil_up_queue(self, stationId: int, queueSize: int) -> None:
		queryQueueSize = select(func.count(1)).select_from(station_queue)\
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)\
			.where(uah_timestamp.is_(None))\
			.where(q_stationFk == stationId)
		countRes = self.conn.execute(queryQueueSize).scalar()
		count = countRes if countRes else 0
		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		songIds = self.get_random_songIds(stationId, deficitSize)
		self.queue_insert_songs(songIds, stationId)


	def __move_from_queue_to_history__(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> int:
		query = select(uah_pk)\
			.join(station_queue, uah_pk == q_userActionHistoryFk)\
			.where(q_stationFk == stationId)\
			.where(q_songFk == songId)\
			.where(uah_queuedTimestamp == queueTimestamp)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)
		userActionId = self.conn.execute(query).scalar_one_or_none()
		if not userActionId:
			return False
		currentTime = self.get_datetime().timestamp()

		histUpdateStmt = update(user_action_history_tbl) \
			.values(timestamp = currentTime) \
			.where(uah_pk == userActionId)
		return self.conn.execute(histUpdateStmt).rowcount

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> bool:
		updCount = self.__move_from_queue_to_history__(
			stationId,
			songId,
			queueTimestamp
		)
		self.fil_up_queue(stationId, self.queue_size)
		self.conn.commit()
		return updCount > 0


	def is_queue_empty(
		self,
		stationId: int,
		offset: int = 0
	) -> bool:
		res = self.queue_count(stationId)
		return res < (offset + 1)


	def get_queue_for_station(
		self,
		stationId: int,
		page: int = 0,
		limit: Optional[int]=None
	) -> Tuple[list[SongListDisplayItem], int]:
		primaryArtistGroupQuery = select(
			func.max(sgar_pk).label("pk"),
			func.max(sgar_isPrimaryArtist).label("isprimary"),
			sgar_songFk.label("songfk")
		).group_by(sgar_songFk)
		#have a default row for songs without any songArtists to match against
		defaultRow = select(literal(-1), literal(None), literal(None))

		subq = union_all(primaryArtistGroupQuery, defaultRow).subquery()

		query = select(
				sg_pk,
				sg_path,
				sg_internalpath,
				sg_name,
				sg_track,
				ab_name.label("album"),
				ar_name.label("artist"),
				uah_queuedTimestamp,
				uah_timestamp
			).select_from(station_queue)\
				.join(user_action_history_tbl,uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.join(albums, sg_albumFk == ab_pk, isouter=True)\
				.join(song_artist, sg_pk == sgar_songFk, isouter=True)\
				.join(artists, sgar_artistFk == ar_pk, isouter=True)\
				.join(subq, subq.c.pk == coalesce(sgar_pk, -1))\
				.where(q_stationFk == stationId)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(uah_timestamp.is_(None))\
				.where(uah_action == UserRoleDef.STATION_REQUEST.value)\
				.order_by(uah_queuedTimestamp)\

		offset = page * limit if limit else 0
		offsetQuery = query.offset(offset)

		if limit:
			offsetQuery = offsetQuery.limit(limit)

		records = self.conn.execute(offsetQuery).mappings()
		result = [SongListDisplayItem(
				id=row[sg_pk],
				name=row[sg_name] or "",
				album=row["album"],
				artist=row["artist"],
				path=row[sg_path],
				internalpath=row[sg_internalpath],
				queuedtimestamp=row[uah_queuedTimestamp],
				playedtimestamp=row[uah_timestamp],
			) for row in records]
		countQuery = select(func.count(1))\
			.select_from(query.subquery())
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def __get_skipped__(
		self,
		stationId: int,
		limit: Optional[int]=None
	) -> Iterator[QueuedItem]:

		query = select(
			q_songFk,
			uah_queuedTimestamp,
		).select_from(station_queue)\
			.join(user_action_history_tbl,uah_pk == q_userActionHistoryFk)\
			.where(q_stationFk == stationId)\
			.where(uah_action == UserRoleDef.STATION_SKIP.value)\
			.order_by(uah_queuedTimestamp)\
			.limit(limit)

		records = self.conn.execute(query)
		for row in records:
			yield QueuedItem(
				id=row[0],
				name="",
				queuedtimestamp=row[1]
			)


	def pop_next_queued(
		self,
		stationId: int,
		loaded: Optional[Set[SongListDisplayItem]]=None,
	) -> SongListDisplayItem:
		if not stationId:
			raise ValueError("Station Id must be provided")

		offset = len(loaded) if loaded else 0

		if self.is_queue_empty(stationId, offset):
			self.fil_up_queue(stationId, self.queue_size + 1 - offset)
			self.conn.commit()


		results, _ = self.get_queue_for_station(
			stationId,
			limit=self.queue_size
		)

		for item in results:
			if loaded and item in loaded:
				continue
			return item

		raise RuntimeError("No unskipped songs available.")


	def __add_song_to_queue__(
		self,
		songId: int,
		stationId: int,
		userId: int,
		trackingInfo: TrackingInfo
	) -> int:
		insertedPk = self.user_actions_history_service.add_user_action_history_item(
			userId,
			UserRoleDef.STATION_REQUEST.value,
			trackingInfo
		)

		if insertedPk:
			stmt = insert(station_queue).values(
				stationfk = stationId,
				songfk = songId,
				useractionhistoryfk = insertedPk
			)
			return self.conn.execute(stmt).rowcount
		else:
			return 0


	def add_to_queue(self,
		itemId: int,
		station: StationInfo,
		user: AccountInfo,
		trackingInfo: TrackingInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST
	):
		songInfo = self.song_info_service.song_info(itemId)
		songName = songInfo.name if songInfo else "Song"
		if station and\
			self.can_song_be_queued_to_station(
				itemId,
				station.id
			):
			self.__add_song_to_queue__(itemId, station.id, user.id, trackingInfo)
			self.conn.commit()
			return
		raise LookupError(f"{songName} cannot be added to {station.name}")


	def queue_count(
		self,
		stationId: int,
	) -> int:
		query = select(func.count(1))\
				.select_from(station_queue)\
				.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.where(q_stationFk == stationId)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(uah_timestamp.is_(None))
		count = self.conn.execute(query).scalar() or 0
		return count


	def get_now_playing_and_queue(
		self,
		stationId: int,
		page: int = 0,
		limit: Optional[int]=50,
		user: Optional[AccountInfo]=None
	) -> CurrentPlayingInfo:
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree(user)
		queue, count = self.get_queue_for_station(
			stationId,
			page,
			limit
		)
		for song in queue:
			if pathRuleTree:
				song.rules = list(pathRuleTree.valuesFlat(song.path))
		playing = next(
			iter(self.get_history_for_station(stationId, limit=1)[0]),
			None
		)
		if pathRuleTree and playing:
				playing.rules = list(pathRuleTree.valuesFlat(playing.path))
		return CurrentPlayingInfo(
			nowplaying=playing,
			items=queue,
			totalrows=count,
			stationrules=[]
		)


	def __mark_queued_song_skipped__(self,
		songId: int,
		queuedTimestamp: float,
		stationId: int
	) -> bool:

		subquery = select(q_userActionHistoryFk)\
			.where(q_stationFk == stationId)\
			.where(q_songFk == songId)

		currentTime = self.get_datetime().timestamp()
		stmt = update(user_action_history_tbl) \
			.values(
				action = UserRoleDef.STATION_SKIP.value,
				timestamp = currentTime
			) \
			.where(
				uah_pk.in_(subquery) #pyright: ignore [reportArgumentType]
			) \
			.where(uah_queuedTimestamp == queuedTimestamp)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)



		updateCount = self.conn.execute(stmt).rowcount

		return updateCount == 1


	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		stationId: int
	) -> Optional[CurrentPlayingInfo]:
		if not self.__mark_queued_song_skipped__(
			songId,
			queuedTimestamp,
			stationId
		):
			return None
		self.fil_up_queue(stationId, self.queue_size)
		self.conn.commit()
		return self.get_now_playing_and_queue(stationId)


	def get_history_for_station(
		self,
		stationId: int,
		page: int = 0,
		limit: Optional[int]=50,
		user: Optional[AccountInfo]=None,
		beforeTimestamp: Optional[float]=None
	) -> Tuple[list[SongListDisplayItem], int]:

		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree(user)

		query = select(
			sg_pk.label("id"),
			uah_queuedTimestamp.label("queuedtimestamp"),
			uah_timestamp.label("playedtimestamp"),
			coalesce[Optional[String]](sg_name, "").label("name"),
			ab_name.label("album"),
			ar_name.label("artist"),
			sg_path.label("path"),
			sg_internalpath.label("internalpath"),
			uah_pk.label("historyid")
		).select_from(station_queue) \
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
			.join(songs, q_songFk == sg_pk) \
			.join(albums, sg_albumFk == ab_pk, isouter=True) \
			.join(song_artist, sg_pk == sgar_songFk, isouter=True) \
			.join(artists, sgar_artistFk == ar_pk, isouter=True) \
			.where(uah_timestamp.isnot(None))\
			.where(q_stationFk == stationId)\
			.where(uah_action == UserRoleDef.STATION_REQUEST.value)\
			.where(uah_timestamp < beforeTimestamp if beforeTimestamp else true)\
			.order_by(desc(uah_timestamp)) \

		offset = page * limit if limit else 0
		offsetQuery = query.offset(offset)
		if limit:
			offsetQuery =	offsetQuery.limit(limit)
		records = self.conn.execute(offsetQuery).mappings()
		result: list[SongListDisplayItem] = []
		for row in records:
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.valuesFlat(cast(str, row["path"])))
			result.append(SongListDisplayItem(**row, rules=rules))
		countQuery = select(func.count(1))\
			.select_from(query.subquery())
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def get_old_last_played(self, stationid: int) -> Iterator[Tuple[int, float]]:
		query = select(
			lp_songFk,
			lp_timestamp
		).where(lp_stationFk == stationid)
		records = self.conn.execute(query)
		yield from ((row[0], row[1]) for row in records)


	def add_to_last_played(
		self,
		stationid: int,
		addura: Iterable[LastPlayedItem]
	) -> int:
		lastPlayedInsert = insert(last_played)
		values: list[dict[str, Any]] = [
			{
				"stationfk": stationid,
				"songfk": e.songid,
				"timestamp": e.timestamp,
			} for e in addura]
		if not values:
			return 0
		return self.conn.execute(lastPlayedInsert, values).rowcount


	def update_last_played_timestamps(
		self,
		stationid: int,
		updatera: Iterable[LastPlayedItem]
	) -> int:
		updateCount = 0
		for item in updatera:
			stmt = update(last_played) \
				.values(timestamp = item.timestamp) \
				.where(lp_stationFk == stationid)\
				.where(lp_songFk == item.songid)
			updateCount += self.conn.execute(stmt).rowcount
		return updateCount


	def trim_recently_played(
		self,
		stationid: int,
		beforeTimestamp: float
	) -> int:
		script = TemplateService.load_sql_script_content(
			SqlScripts.TRIM_STATION_QUEUE_HISTORY
		)
		count = self.conn.exec_driver_sql(script, {
			"action": UserRoleDef.STATION_REQUEST.value,
			"stationid": stationid,
			"timestamp": beforeTimestamp
		}).rowcount
		return count


	def squish_station_history(
		self,
		stationid: int,
		beforeTimestamp: float
	) -> Tuple[int, int, int]:
		unsquashed, _ = self.get_history_for_station(
			stationid,
			limit=None,
			beforeTimestamp=beforeTimestamp
		)

		squashed = {row[0]:row[1] for row in self.get_old_last_played(stationid)}
		addura = [v for v in {
			e.id:LastPlayedItem(
				songid = e.id,
				timestamp = e.playedtimestamp or 0,
				historyid = e.historyid or 0
			)
			for e in reversed(unsquashed) if e.id not in squashed
		}.values()]
		updatera = (v for v in {
			e.id:LastPlayedItem(
				songid = e.id,
				timestamp = e.playedtimestamp or 0,
				historyid = e.historyid or 0
			)
			for e in reversed(unsquashed)
			if e.id in squashed and e.playedtimestamp and
				squashed[e.id] < e.playedtimestamp
		}.values())
		addedCount = self.add_to_last_played(stationid, addura)
		updatedCount = self.update_last_played_timestamps(stationid, updatera)
		deletedCount = self.trim_recently_played(stationid, beforeTimestamp)
		self.conn.commit()
		return (addedCount, updatedCount, deletedCount)


	def can_song_be_queued_to_station(self, songId: int, stationId: int) -> bool:
		query = select(func.count(1)).select_from(stations_songs_tbl)\
			.join(songs, stsg_songFk == sg_pk)\
			.join(stations_tbl, st_pk == stsg_stationFk)\
			.where(st_typeid == StationTypes.SONGS_ONLY.value)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(stsg_songFk == songId)\
			.where(stsg_stationFk == stationId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False
	
	def get_catalogue(
		self,
		stationId: int,
		page: int = 0,
		name: str = "",
		parentName: str = "",
		creator: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[CatalogueItem], int]:
		songs, count = self.song_info_service.get_fullsongs_page(
			stationId,
			page,
			name,
			parentName,
			creator,
			limit,
			user
		)

		return [CatalogueItem(
			id=s.id,
			name=s.name or "Missing Name",
			itemtype="Songs",
			requesttypeid=StationTypes.SONGS_ONLY.value,
			queuedtimestamp=0,
			parentName=s.album.name if s.album else "No Album",
			creator=s.primaryartist.name 
				if s.primaryartist 
				else next((a.name for a in s.artists or []), ""),
			rules=s.rules
		) for s in songs], count


	def accepted_request_types(self) -> set[StationRequestTypes]:
		return { StationRequestTypes.SONG }