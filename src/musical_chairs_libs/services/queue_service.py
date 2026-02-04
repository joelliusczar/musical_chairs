#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
#import musical_chairs_libs.dtos_and_utilities.logging as logging
import json
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
	Iterable,
)
from sqlalchemy import (
	and_,
	distinct,
	desc,
	func,
	insert,
	Label,
	or_,
	select,
	update,
	true,
	String
)
from pathlib import Path
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import coalesce
from .station_service import StationService
from .song_info_service import SongInfoService
from .path_rule_service import PathRuleService
from .current_user_provider import CurrentUserProvider
from musical_chairs_libs.tables import (
	songs,
	stations,
	stations_songs as stations_songs_tbl, stsg_stationFk, stsg_songFk, 
	stsg_lastplayednum,
	station_queue, q_pk, q_songFk, q_stationFk, q_timestamp, q_queuedTimestamp,
	q_itemType, q_parentKey, q_action,
	albums,
	artists,
	song_artist,
	sgar_songFk, sgar_artistFk, sgar_isPrimaryArtist,
	sg_pk, sg_name, sg_path, sg_albumFk, sg_internalpath, sg_deletedTimstamp,
	stations as stations_tbl, st_pk, st_typeid, st_playnum,
	ar_pk, ar_name,
	ab_pk, ab_name,
	last_played, lp_songFk, lp_stationFk, lp_timestamp, lp_itemType, lp_parentKey
)
from musical_chairs_libs.dtos_and_utilities import (
	CatalogueItem,
	ConfigAcessors,
	CurrentPlayingInfo,
	HistoryItem,
	get_datetime,
	logging,
	SongListDisplayItem,
	StationInfo,
	LastPlayedItem,
	OwnerInfo,
	normalize_opening_slash,
	QueuePossibility,
	QueueMetrics,
	SimpleQueryParameters,
	StationCreationInfo,
	StreamQueuedItem,
)
from musical_chairs_libs.protocols import (
	SongPopper,
	RadioPusher,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationActions,
	StationRequestTypes,
	StationsSongsActions,
	StationTypes
)
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)


played_count_query = select(
	q_stationFk.label("countedstationid"),
	q_songFk.label("countedsongid"),
	func.count(q_pk).label("count")
)\
	.group_by(q_stationFk, q_songFk)

played_count_cte = played_count_query.cte("playedcounts")
counted_song_id = played_count_cte.c.countedsongid


def choice(
	items: Sequence[Any],
	sampleSize: int,
	weights: Sequence[float]
) -> Collection[Any]:
	# the sum of weights needs to equal 1
	return numpy_choice(
		items,
		sampleSize,
		p = cast(Any,weights),
		replace=False
	).tolist()

class QueueService(SongPopper, RadioPusher):

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		songInfoService: SongInfoService,
		pathRuleService: PathRuleService,
		stationService: Optional[StationService]=None,
		choiceSelector: Optional[
			Callable[[Sequence[Any], int, Sequence[float]], Collection[Any]]
		]=None,
		queueSize: int = 50
	) -> None:
			if not conn:
				raise RuntimeError("No connection provided")
			if not stationService:
				stationService = StationService(
					conn,
					currentUserProvider,
					pathRuleService
				)
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.current_user_provider = currentUserProvider
			self.station_service = stationService
			self.song_info_service = songInfoService
			self.choice = choiceSelector
			self.get_datetime = get_datetime
			self.path_rule_service = pathRuleService
			self.queue_size = queueSize


	def get_all_station_possibilities(
		self, stationPk: int
	) -> list[tuple[QueuePossibility,StreamQueuedItem]]:
		groupColumns: list[Label[Any]] = [
			sg_pk.label("id"),
			stsg_lastplayednum.label("lastplayednum"),
			st_playnum.label("playnum"),
			sg_internalpath.label("internalpath"),
			sg_path.label("treepath"),
			coalesce(sg_name, "").label("name"),
			coalesce(ab_name, "").label("album.name"),
			coalesce(ar_name, "").label("artist.name"),
		]
		query = select(
			*groupColumns,
			func.row_number().over(
				partition_by=sg_pk,
				order_by=(desc(sgar_isPrimaryArtist), desc(ar_pk))
			).label("artistrank"),
		) \
			.select_from(stations) \
			.join(stations_songs_tbl, st_pk == stsg_stationFk) \
			.join(songs, sg_pk == stsg_songFk) \
			.outerjoin(albums, sg_albumFk == ab_pk)\
			.outerjoin(song_artist, sg_pk == sgar_songFk)\
			.outerjoin(artists, sgar_artistFk == ar_pk)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationPk) \
			.group_by(*groupColumns)\
			.order_by(
				desc(stsg_lastplayednum),
				func.rand()
			)

		rows = self.conn.execute(
			query.select().where(query.c.artistrank == 1)
		).mappings().fetchall()
		return [
			(
				QueuePossibility(
					itemId=r["id"],
					lastplayednum=r["lastplayednum"], 
					playnum=r["playnum"]
				),
				StreamQueuedItem(
					id=r["id"],
					name=r["name"],
					queuedtimestamp=self.get_datetime().timestamp(),
					itemtype=StationRequestTypes.SONG.lower(),
					album=r["album.name"],
					artist=r["artist.name"],
					internalpath=r["internalpath"],
					treepath=r["treepath"],
					userId=None
				)
			) \
				for r in rows
			]


	def get_random_songIds(
		self,
		stationId: int,
		queueMetrics: QueueMetrics
	) -> Collection[StreamQueuedItem]:
		def weigh(n: float) -> float:
			return n * n
		rows = self.get_all_station_possibilities(stationId)
		room = min(len(rows), queueMetrics.maxSize)
		if not room:
			raise RuntimeError("No song possibilities were found")
		deficitSize = room - queueMetrics.queued - queueMetrics.loaded
		if deficitSize < 1:
			return []
		playNum = rows[0][0].playnum or 1 if len(rows) > 1 else 1
		ages = [(playNum - r[0].lastplayednum) for r in rows]
		total = sum((weigh(a) for a in ages))
		weights = [weigh(a)/total for a in ages] \
			if total != 0 else [1/len(ages) for _ in range(1, len(ages) + 1)]
		zeroCount = sum(1 for w in weights if w == 0)
		sampleSize = deficitSize if deficitSize < len(rows) - zeroCount \
			else len(rows) - zeroCount
		songMap = {r[0].itemId:r[1] for r in rows}
		
		try:
			selection = self.choice(list(songMap.keys()), sampleSize, weights)
			return [songMap[s] for s in selection]
		except Exception as e:
			logging.radioLogger.error(e, exc_info=True)
			logging.radioLogger.error([r[0].itemId for r in rows])
			logging.radioLogger.error(ages)
			logging.radioLogger.error(weights)
			logging.radioLogger.error(sum(weights))
			raise


	def queue_file_name(self, station: StationInfo) -> str:
		if not station.owner:
			raise RuntimeError("Station owner is not loaded")
		
		filePath = f"{ConfigAcessors.station_queue_files_dir()}"\
			f"/{station.owner.username}/{station.name}.jsonl"
		Path(filePath).parent.mkdir(parents=True, exist_ok=True)
		return filePath


	def load_current_queue(
		self,
		station: StationInfo
	) -> Iterator[StreamQueuedItem]:
		filePath = self.queue_file_name(station)
		try:
			with open(filePath, "r", 1) as f:
				while line := f.readline():
					yield StreamQueuedItem(**json.loads(line))
		except FileNotFoundError:
			return


	def replace_queue_file(
		self,
		station: StationInfo,
		songs: Iterable[StreamQueuedItem]
	):
		filePath = self.queue_file_name(station)
		
		with open(filePath, "w", 1) as f:
			for song in songs:
				f.write(json.dumps(song.model_dump()) + "\n")



	def queue_insert_songs(
		self,
		alreadyQueued: list[StreamQueuedItem],
		queueRequests: Collection[StreamQueuedItem],
		station: StationInfo,
	):

		for i, request in enumerate(queueRequests):
			if station.typeid == StationTypes.SONGS_ONLY.value:
				lastPlayedUpdate = update(stations_songs_tbl)\
					.values(lastplayednum = station.playnum + i + 1) \
					.where(stsg_stationFk == station.id)\
					.where(stsg_songFk == request.id)
				self.conn.execute(lastPlayedUpdate)

		alreadyQueued.extend(queueRequests)

		self.__add_to_station_playnum__(station, len(queueRequests))


	def __get_station__(self, stationId: int) -> StationInfo:
		return next(self.station_service.get_stations_unsecured(stationId))


	def __add_to_station_playnum__(self, station: StationInfo, addition: int):
		self.station_service.update_station(StationCreationInfo(
				**station.model_dump(exclude={"id", "playnum"}),
				playnum=station.playnum + addition,
			),
			station.id,
		)	


	def fil_up_queue(
		self,
		station: StationInfo,
		queueMetrics: QueueMetrics,
		alreadyQueued: list[StreamQueuedItem] | None = None
	) -> None:
		
		if alreadyQueued is None:
			alreadyQueued = []

		countRes = sum(1 for s in alreadyQueued \
			if s.action != StationActions.STATION_SKIP.value
		)
		count = countRes if countRes else 0
		queueMetrics.queued = count
		songs = self.get_random_songIds(station.id, queueMetrics)
		
		if songs:
			self.queue_insert_songs(
				alreadyQueued,
				songs,
				station
			)

		self.replace_queue_file(station, alreadyQueued)


	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> bool:
		station = self.__get_station__(stationId)
		alreadyQueued = [*self.load_current_queue(station)]
		completedIdx = next(
			(i for i,e in enumerate(alreadyQueued)\
				if e.id == songId and e.queuedtimestamp == queueTimestamp
			),
			None
		)
		if completedIdx is None:
			return False
		completed = alreadyQueued[completedIdx]

		stmt = insert(station_queue).values(
			stationfk = stationId,
			songfk = songId,
			action = completed.action or StationsSongsActions.PLAYED.value,
			queuedtimestamp = completed.queuedtimestamp,
			playedtimestamp = self.get_datetime().timestamp(),
			userfk = completed.userId
		)
		try:
			self.conn.execute(stmt)
		except IntegrityError as e:
			logging.radioLogger.error(e, exc_info=True)
			return False
		queueMetrics = QueueMetrics(maxSize=self.queue_size)
		alreadyQueued.pop(completedIdx)
		self.fil_up_queue(station, queueMetrics, alreadyQueued)
		self.conn.commit()
		return completed.action != StationsSongsActions.SKIP.value


	def get_queue_for_station(
		self,
		stationId: int,
		page: int = 0,
		limit: int | None=None
	) -> Tuple[list[StreamQueuedItem], int]:
		station = self.__get_station__(stationId)
		queued = [*self.load_current_queue(station)]
		return queued, len(queued)


	def pop_next_queued(
		self,
		stationId: int,
		loaded: Set[StreamQueuedItem] | None=None,
	) -> StreamQueuedItem | None:
		if not stationId:
			raise ValueError("Station Id must be provided")
		
		if self.conn.closed:
			#this method will sometimes get called before the calling code realizes
			#the connection is closed
			return

		offset = len(loaded) if loaded else 0
		station = self.__get_station__(stationId)
		alreadyQueued = [*self.load_current_queue(station)]

		if (len(alreadyQueued) - offset) < 1:
			queueMetrics = QueueMetrics(maxSize=self.queue_size + 1, loaded=offset)
			self.fil_up_queue(station, queueMetrics, alreadyQueued)
			self.conn.commit()


		for item in alreadyQueued:
			if loaded and item in loaded:
				continue
			return item

		raise RuntimeError("No unskipped songs available.")


	"""
		This is mostly used in testing
	"""
	def __move_next__(self, stationId: int):
		item = self.pop_next_queued(stationId)
		# queue = self.get_queue_for_station(stationId)[0]
		if item:
			playing = item
			self.move_from_queue_to_history(
				stationId,
				playing.id,
				playing.queuedtimestamp
			)


	def __add_song_to_queue__(
		self,
		song: StreamQueuedItem,
		station: StationInfo,
	):

		filePath = self.queue_file_name(station)
		
		with open(filePath, "a", 1) as f:
			f.write(json.dumps(song.model_dump()) + "\n")


	def add_to_queue(self,
		itemId: int,
		station: StationInfo,
		#stationItemType is required for interface compliance
		stationItemType: StationRequestTypes=StationRequestTypes.SONG
	):
		songInfo = self.song_info_service.song_info(itemId)
		songName = songInfo.name if songInfo else "song"
		if station and songInfo\
			and self.can_song_be_queued_to_station(
				itemId,
				station.id
			):

			self.__add_song_to_queue__(
				StreamQueuedItem(**songInfo.model_dump(
					include={f for f in StreamQueuedItem.model_fields}
				)),
				station
			)
			return
		raise LookupError(f"{songName} cannot be added to {station.name}")


	def get_now_playing_and_queue(
		self,
		station: StationInfo,
		page: int = 0,
		limit: Optional[int]=50
	) -> CurrentPlayingInfo:
		pathRuleTree = None
		user = self.current_user_provider.current_user()
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree()
		queue, count = self.get_queue_for_station(
			station.id,
			page,
			limit
		)
		ruled = [SongListDisplayItem(**s.model_dump()) for s in queue\
			if s.action != StationsSongsActions.SKIP.value
		]
		for song in ruled:
			if pathRuleTree:
				song.rules = list(pathRuleTree.values_flat(
					normalize_opening_slash(song.treepath)
				))
		playing = next(
			iter(self.get_history_for_station(station, limit=1)[0]),
			None
		)
		if pathRuleTree and playing:
				playing.rules = list(pathRuleTree.values_flat(
					normalize_opening_slash(playing.treepath)
				))
		return CurrentPlayingInfo(
			nowplaying=playing,
			items=ruled,
			totalrows=count,
			stationrules=station.rules
		)


	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		station: StationInfo,
	) -> Optional[CurrentPlayingInfo]:
		alreadyQueued = [*self.load_current_queue(station)]
		skipIdx = next(
			(i for i,e in enumerate(alreadyQueued)\
				if e.id == songId and e.queuedtimestamp == queuedTimestamp
			),
			None
		)
		if skipIdx is None:
			raise RuntimeError(
				f"{songId} at {queuedTimestamp} could not be found to be skipped"
			)
		alreadyQueued[skipIdx].action = StationsSongsActions.SKIP.value
		queueMetrics = QueueMetrics(maxSize=self.queue_size)
		self.fil_up_queue(station, queueMetrics, alreadyQueued)
		self.conn.commit()
		return self.get_now_playing_and_queue(station)


	def get_history_for_station(
		self,
		station: StationInfo,
		page: int = 0,
		limit: Optional[int]=50,
		beforeTimestamp: Optional[float]=None
	) -> Tuple[list[HistoryItem], int]:

		user = self.current_user_provider.current_user()
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree()

		query = select(
			sg_pk.label("id"),
			q_queuedTimestamp.label("queuedtimestamp"),
			q_timestamp.label("playedtimestamp"),
			coalesce[Optional[String]](sg_name, "").label("name"),
			ab_name.label("album"),
			ar_name.label("artist"),
			sg_path.label("treepath"),
			sg_internalpath.label("internalpath"),
			q_pk.label("historyid"),
			q_itemType.label("itemtype"),
			q_parentKey.label("parentkey"),
		).select_from(station_queue) \
			.join(songs, q_songFk == sg_pk) \
			.join(albums, sg_albumFk == ab_pk, isouter=True) \
			.join(song_artist, sg_pk == sgar_songFk, isouter=True) \
			.join(artists, sgar_artistFk == ar_pk, isouter=True) \
			.where(q_timestamp.isnot(None))\
			.where(q_stationFk == station.id)\
			.where(
				or_(
					q_action.is_(None),
					q_action == StationsSongsActions.PLAYED.value
			))\
			.where(q_timestamp < beforeTimestamp if beforeTimestamp else true)\
			.order_by(desc(q_timestamp)) \

		offset = page * limit if limit else 0
		offsetQuery = query.offset(offset)
		if limit:
			offsetQuery =	offsetQuery.limit(limit)
		records = self.conn.execute(offsetQuery).mappings()
		result: list[HistoryItem] = []
		for row in records:
			rules = []
			if pathRuleTree:
				rules = list(pathRuleTree.values_flat(
					normalize_opening_slash(cast(str, row["treepath"])))
				)
			result.append(HistoryItem(**row, rules=rules))
		countQuery = select(func.count(1))\
			.select_from(query.subquery())
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count


	def get_old_last_played(self, stationid: int) -> Iterator[LastPlayedItem]:
		query = select(
			lp_songFk,
			lp_timestamp,
			lp_itemType,
			lp_parentKey,
		).where(lp_stationFk == stationid)
		records = self.conn.execute(query)
		yield from (LastPlayedItem(
			songid=row[0],
			timestamp=row[1],
			historyid=0,
			itemtype=row[2],
			parentkey=row[3]
		) for row in records)


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
				"itemtype": e.itemtype,
				"parentkey": e.parentkey
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
				.values(playedtimestamp = item.timestamp) \
				.where(lp_stationFk == stationid)\
				.where(lp_songFk == item.songid)\
				.where(lp_itemType == item.itemtype)\
				.where(lp_parentKey == item.parentkey)
			updateCount += self.conn.execute(stmt).rowcount
		return updateCount


	def trim_recently_played(
		self,
		stationid: int,
		beforeTimestamp: float
	) -> int:

		count = self.conn.exec_driver_sql(
"""
CREATE OR REPLACE TEMPORARY TABLE `historyids` (
	`pk` int(11), KEY `pk`(`pk`) USING HASH
) ENGINE=MEMORY
SELECT Q.`pk` FROM `stationlogs` Q
WHERE Q.`playedtimestamp` < %(timestamp)s
AND Q.`stationfk` = %(stationid)s;

DELETE FROM `stationlogs` WHERE `pk` IN (SELECT `pk` FROM `historyids`);

"""
			, {
			"stationid": stationid,
			"timestamp": beforeTimestamp
		}).rowcount
		return count


	def squish_station_history(
		self,
		station: StationInfo,
		beforeTimestamp: float
	) -> Tuple[int, int, int]:
		unsquashed, _ = self.get_history_for_station(
			station,
			limit=None,
			beforeTimestamp=beforeTimestamp
		)

		squashed = {
			(item.songid, item.itemtype, item.parentkey):item.timestamp
			for item in self.get_old_last_played(station.id)
		}
		addura = [v for v in {
			e.id:LastPlayedItem(
				songid = e.id,
				timestamp = e.playedtimestamp or 0,
				historyid = e.historyid or 0,
				itemtype = e.itemtype,
				parentkey = e.parentkey
			)
			for e in reversed(unsquashed) 
				if (e.id, e.itemtype, e.parentkey) not in squashed
		}.values()]
		updatera = (v for v in {
			e.id:LastPlayedItem(
				songid = e.id,
				timestamp = e.playedtimestamp or 0,
				historyid = e.historyid or 0,
				itemtype = e.itemtype,
				parentkey = e.parentkey
			)
			for e in reversed(unsquashed)
			if (e.id, e.itemtype, e.parentkey) in squashed and e.playedtimestamp and
				squashed[(e.id, e.itemtype, e.parentkey)] < e.playedtimestamp
		}.values())
		addedCount = self.add_to_last_played(station.id, addura)
		updatedCount = self.update_last_played_timestamps(station.id, updatera)
		deletedCount = self.trim_recently_played(station.id, beforeTimestamp)
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
		queryParams: Optional[SimpleQueryParameters]=None,
		name: str = "",
		parentname: str = "",
		creator: str = "",
	) -> Tuple[list[CatalogueItem], int]:

		if not queryParams:
			queryParams = SimpleQueryParameters()

		query = self.song_info_service.full_song_base_query(
			stationId=stationId,
			song=name,
			album=parentname,
			artist=creator
		)

		countQuery = query.with_only_columns(func.count(distinct(sg_pk)))

		count = self.conn.execute(countQuery).scalar() or 0

		cte = query\
			.outerjoin(
				played_count_cte,
				and_(
					played_count_cte.c.countedsongid == sg_pk,
					played_count_cte.c.countedstationid == stsg_stationFk
				)
			)\
			.with_only_columns(
				sg_pk.label("id"),
				sg_path.label("treepath"),
				coalesce(sg_name, "Missing Name").label("name"),
				coalesce(ab_name, "No Album").label("parentname"),
				coalesce(ar_name,"").label("creator"),
				func.row_number().over(
					partition_by=sg_pk,
					order_by=(desc(sgar_isPrimaryArtist), desc(ar_pk))
				).label("artistrank"),
				coalesce(played_count_cte.c.count, 0).label("playedcount"),  
			).cte()
		
		offset = queryParams.page * queryParams.limit if queryParams.limit else 0
		cte_query = cte\
			.select()\
			.where(cte.c.artistrank == 1)\
			.with_only_columns(
				cte.c.id,
				cte.c.name,
				cte.c.treepath,
				cte.c.parentname,
				cte.c.creator,
				cte.c.playedcount
			)

		if queryParams.sortdir == "dsc" and queryParams.orderby:
			ordered_query = cte_query.order_by(desc(queryParams.orderby))
		else:
			ordered_query = cte_query.order_by(queryParams.orderby)
			
		ordered_query = ordered_query.offset(offset).limit(queryParams.limit)
		

		records = self.conn.execute(ordered_query).mappings()

		user = self.current_user_provider.current_user(optional=True)
		pathRuleTree = None
		if user:
			pathRuleTree = self.path_rule_service.get_rule_path_tree()


		return [CatalogueItem(
			id=s["id"],
			name=s["name"],
			itemtype=StationRequestTypes.SONG.lower(),
			requesttypeid=StationTypes.SONGS_ONLY.value,
			queuedtimestamp=0,
			parentname=s["parentname"],
			creator=s["creator"],
			rules=list(pathRuleTree.values_flat(
					normalize_opening_slash(cast(str, s["treepath"])))
				) if pathRuleTree else [],
			owner=OwnerInfo(id=0, username="", displayname="NA"),
			playedcount=s["playedcount"]
		) for s in records], count


	def accepted_request_types(self) -> set[StationRequestTypes]:
		return { StationRequestTypes.SONG }