from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	clean_search_term_for_like,
	get_datetime,
	logging,
	SongListDisplayItem,
	StationInfo,
	UserRoleDef,
	RulePriorityLevel,
	CatalogueItem,
	CurrentPlayingInfo,
	QueueRequest,
	OwnerInfo,
	SimpleQueryParameters,
	UserRoleDomain,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationTypes,
	StationRequestTypes
)
from musical_chairs_libs.protocols import SongPopper, RadioPusher
from musical_chairs_libs.tables import (
	albums as albums_tbl, ab_pk, ab_name, ab_year, ab_albumArtistFk, ab_ownerFk,
	artists as artists_tbl, ar_pk, ar_name,
	songs,
	stations as stations_tbl, st_typeid,
	user_action_history as user_action_history_tbl, uah_pk, uah_queuedTimestamp,
	uah_timestamp, uah_action,
	station_queue, q_userActionHistoryFk, q_songFk, q_stationFk, q_parentKey,
	q_itemType,
	sg_disc, sg_pk, sg_albumFk, sg_deletedTimstamp,
	sg_trackNum,
	st_pk,
	last_played, lp_stationFk, lp_timestamp, lp_itemType, lp_parentKey,
	stations_albums as stations_albums_tbl, stab_albumFk, stab_stationFk,
	users as users_tbl, u_pk, u_username, u_displayName
)
from .current_user_provider import CurrentUserProvider
from .queue_service import QueueService
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)
from sqlalchemy import (
	desc,
	select,
	func,
	update,
	distinct,
	or_,
)
from sqlalchemy.engine import Connection
from sqlalchemy.sql.functions import coalesce
from typing import (
	Any,
	Callable,
	Optional,
	cast,
	Collection,
	Iterator,
	Sequence,
	Set,
	Tuple,
)

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


class AlbumQueueService(SongPopper, RadioPusher):

	def __init__(
		self,
		conn: Connection,
		queueService: QueueService,
		currentUserProvider: CurrentUserProvider,
		choiceSelector: Optional[
			Callable[[Sequence[Any], int, Sequence[float]], Collection[Any]]
		]=None,
		queueSize: int = 3
	) -> None:
			if not conn:
				raise RuntimeError("No connection provided")
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.queue_service = queueService
			self.choice = choiceSelector
			self.get_datetime = get_datetime
			self.current_user_provider = currentUserProvider
			self.queue_size = queueSize

	@staticmethod
	def get_station_possibilities_query(
		stationid: int
	):
		query = select(stab_albumFk, func.max(coalesce(uah_queuedTimestamp, 0))) \
			.select_from(stations_tbl) \
			.join(stations_albums_tbl, st_pk == stab_stationFk) \
			.join(songs, sg_albumFk == stab_albumFk) \
			.join(station_queue, (q_stationFk == st_pk) \
				& (q_parentKey == stab_albumFk) \
				& (q_itemType == StationRequestTypes.ALBUM.lower()), isouter=True) \
			.join(last_played, (lp_stationFk == st_pk) \
				& (lp_parentKey == stab_albumFk)
				& (lp_itemType == StationRequestTypes.ALBUM.lower()), isouter=True
			)\
			.join(user_action_history_tbl,
				(uah_pk == q_userActionHistoryFk),
				isouter=True
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationid) \
			.group_by(stab_albumFk) \
			.order_by(
				desc(func.max(coalesce(uah_queuedTimestamp, 0))),
				desc(func.max(coalesce(uah_timestamp, 0))),
				desc(coalesce(lp_timestamp, 0)),
				func.rand()
			)
		return query

	def get_all_station_possibilities(
		self,
		stationid: int
	) -> Iterator[Tuple[int, float]]:

		query = self.get_station_possibilities_query(stationid)

		rows = self.conn.execute(query)
		yield from ((row[0], row[1]) for row in rows)

	def get_random_albumIds(
		self,
		stationId: int,
		deficitSize: int
	) -> Collection[int]:
		def weigh(n: float) -> float:
			return n * n
		rows = [*self.get_all_station_possibilities(stationId)]
		mostRecentDraw = rows[0][1] or self.get_datetime().timestamp() \
			if len(rows) > 1 else self.get_datetime().timestamp()
		ages = [(mostRecentDraw - r[1] or 0) for r in rows]
		total = sum(
			(weigh(a) for a in ages)
		)
		weights = [weigh(a)/total for a in ages]
		zeroCount = sum(1 for w in weights if w == 0)
		sampleSize = deficitSize if deficitSize < len(rows) - zeroCount \
			else len(rows) - zeroCount
		ids = [r[0] for r in rows]
		if not ids:
			raise RuntimeError("No playlist possibilities were found")
		try:
			selection = self.choice(ids, sampleSize, weights)
			return selection
		except:
			logging.radioLogger.error(rows)
			logging.radioLogger.error(ages)
			logging.radioLogger.error(weights)
			logging.radioLogger.error(sum(weights))
			raise
	
	def queue_count(
		self,
		stationId: int,
	) -> int:
		query = select(func.count(distinct(sg_albumFk)))\
				.select_from(station_queue)\
				.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.where(q_stationFk == stationId)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(uah_timestamp.is_(None))
		count = self.conn.execute(query).scalar() or 0
		return count

	def fil_up_queue(self, stationId: int, queueSize: int) -> None:
		
		count = self.queue_count(stationId)

		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		albumIds = self.get_random_albumIds(stationId, deficitSize)
		songAlbumQuery = select(sg_pk, sg_albumFk, sg_disc, sg_trackNum)\
			.where(sg_albumFk.in_(albumIds))\
			.where(sg_deletedTimstamp.is_(None))
		
		songTuples = self.conn.execute(songAlbumQuery).fetchall()
		sortMap = {a[1]:a[0] for a in enumerate(albumIds)}
		sortedSongs = sorted(
			(r for r in songTuples),
			key=lambda r: (sortMap[r[1]], r[2] or 0, r[3])
		)
		self.queue_service.queue_insert_songs(
			[QueueRequest(
				id=r[0],
				parentKey=r[1],
				itemtype=StationRequestTypes.ALBUM.lower()
			) for r in sortedSongs],
			stationId
		)

	def add_to_queue(
		self,
		itemId: int,
		station: StationInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST
	):
		if station and\
			self.can_album_be_queued_to_station(
				itemId,
				station.id,
			):
			query = select(sg_pk)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(sg_albumFk == itemId)
			
			rows = self.conn.execute(query)
			self.queue_service.queue_insert_songs(
				[QueueRequest(
					id=r[0],
					itemtype=StationRequestTypes.ALBUM.lower(),
					parentKey=itemId
				) for r in rows],
				station.id,
			)
			self.conn.commit()
			return
		raise LookupError(f"album cannot be added to {station.name}")
	
	def can_album_be_queued_to_station(
		self,
		albumId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_albums_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(stab_stationFk == stationId)\
			.where(or_(
				st_typeid == StationTypes.ALBUMS_ONLY.value,
				st_typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value
			))\
			.where(stab_albumFk == albumId)
		
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	def is_queue_empty(
		self,
		stationId: int,
		offset: int = 0,
	) -> bool:
		res = self.queue_count(stationId)
		return res < (offset + 1)

	def pop_next_queued(
		self,
		stationId: int,
		loaded: Optional[Set[SongListDisplayItem]]=None
	) -> SongListDisplayItem:
		if not stationId:
			raise ValueError("Station Id must be provided")

		# songOffset = len(loaded) if loaded else 0
		albumOffset = len({(l.parentkey, l.itemtype) for l in loaded})\
			if loaded else 0

		if self.is_queue_empty(stationId, albumOffset):
			self.fil_up_queue(stationId, self.queue_size + 1 - albumOffset)
			self.conn.commit()


		results, _ = self.queue_service.get_queue_for_station(
			stationId,
			limit=self.queue_service.queue_size
		)

		for item in results:
			if loaded and item in loaded:
				continue
			return item

		raise RuntimeError("No unskipped songs available.")
	


	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float,
	) -> bool:
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
		updCount = self.conn.execute(histUpdateStmt).rowcount
		self.fil_up_queue(stationId, self.queue_size)
		self.conn.commit()
		return updCount > 0
	
	def get_catalogue(
		self,
		stationId: int,
		queryParams: Optional[SimpleQueryParameters]=None,
		name: str = "",
		parentname: str = "",
		creator: str = "",
	) -> Tuple[list[CatalogueItem], int]:
		if queryParams is None:
			queryParams = SimpleQueryParameters()
		offset = queryParams.page * queryParams.limit if queryParams.limit else 0
		lcollection = clean_search_term_for_like(name)
		lcreator = clean_search_term_for_like(creator)

		query = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ar_name.label("creator"),
			ab_year.label("year"),
			ab_ownerFk.label("ownerid"),
			u_username,
			u_displayName,
		)\
			.select_from(stations_tbl) \
			.join(stations_albums_tbl, st_pk == stab_stationFk) \
			.join(albums_tbl, stab_albumFk == ab_pk) \
			.join(artists_tbl, ab_albumArtistFk == ar_pk, isouter=True) \
			.join(users_tbl, u_pk == ab_ownerFk, isouter=True)\
			.where(st_pk == stationId)
		
		if lcollection:
			query = query.where(ab_name.like(f"%{lcollection}%"))

		if lcreator:
			query = query.where(ar_name.like(f"%{lcreator}%"))

		limitedQuery = query\
			.offset(offset)\
			.limit(queryParams.limit)

		records = self.conn.execute(limitedQuery).mappings()

		userId = self.current_user_provider.optional_user_id()
		result = [CatalogueItem(
			id=r["id"],
			name=r["name"] or "",
			parentname="",
			creator=r["creator"] or "",
			itemtype="Album",
			requesttypeid=StationTypes.ALBUMS_ONLY.value,
			queuedtimestamp=0,
			rules=[] if userId and r["ownerid"] != userId else [
				ActionRule(
					domain=UserRoleDomain.Album.value,
					name=UserRoleDef.ALBUM_EDIT.value,
					priority=RulePriorityLevel.OWNER.value
				)
			],
			owner=OwnerInfo(
				id=r["ownerid"],
				username=r[u_username],
				displayname=r[u_displayName]
			)
			) for r in records]
		countQuery = select(func.count(1))\
			.select_from(cast(Any, query))
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count
	
	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		station: StationInfo,
	) -> Optional[CurrentPlayingInfo]:
		if not self.queue_service.__mark_queued_song_skipped__(
			songId,
			queuedTimestamp,
			station.id
		):
			return None
		self.fil_up_queue(station.id, self.queue_size)
		self.conn.commit()
		return self.queue_service.get_now_playing_and_queue(station)
	
	def accepted_request_types(self) -> set[StationRequestTypes]:
		return { StationRequestTypes.ALBUM }