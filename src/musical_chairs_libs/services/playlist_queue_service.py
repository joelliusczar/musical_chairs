from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	clean_search_term_for_like,
	get_datetime,
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
	StationRequestTypes,
	StationTypes,
)
from musical_chairs_libs.protocols import SongPopper, RadioPusher
from sqlalchemy.sql.functions import coalesce
from musical_chairs_libs.tables import (
	songs,
	stations as stations_tbl, st_typeid,
	user_action_history as user_action_history_tbl, uah_pk, uah_queuedTimestamp,
	uah_timestamp, uah_action,
	users as users_tbl, u_pk, u_displayName, u_username,
	station_queue, q_userActionHistoryFk, q_songFk, q_stationFk, q_parentKey,
	q_itemType,
	sg_pk, sg_deletedTimstamp,
	st_pk,
	last_played, lp_stationFk, lp_timestamp, lp_itemType, lp_parentKey,
	playlists as playlists_tbl, pl_pk, pl_ownerFk, pl_name, 
	stab_stationFk,
	stations_playlists as stations_playlists_tbl, stpl_playlistFk, stpl_stationFk,
	playlists_songs as playlists_songs_tbl, plsg_songFk, plsg_playlistFk,
	plsg_lexorder,
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
	distinct,
	update,
	or_,
)
from sqlalchemy.engine import Connection
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

class PlaylistQueueService(SongPopper, RadioPusher):

	def __init__(
		self,
		conn: Connection,
		queueService: QueueService,
		currentUserProvider: CurrentUserProvider,
		choiceSelector: Optional[
			Callable[[Sequence[Any], int, Sequence[float]], Collection[Any]]
		]=None,
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
			self.queue_size = 3

	@staticmethod
	def get_station_possibilities_query(stationid: int):
		query = select(stpl_playlistFk, func.max(coalesce(uah_queuedTimestamp))) \
			.select_from(stations_tbl) \
			.join(stations_playlists_tbl, st_pk == stpl_stationFk) \
			.join(playlists_songs_tbl, plsg_playlistFk == stpl_playlistFk) \
			.join(songs, sg_pk == plsg_songFk) \
			.join(station_queue, (q_stationFk == st_pk) \
				& (q_parentKey == stpl_playlistFk) \
				& (q_itemType == StationRequestTypes.PLAYLIST.lower()), isouter=True) \
			.join(last_played, (lp_stationFk == st_pk) \
				& (lp_parentKey == stpl_playlistFk)
				& (lp_itemType == StationRequestTypes.PLAYLIST.lower()), isouter=True
			)\
			.join(user_action_history_tbl,
				(uah_pk == q_userActionHistoryFk),
				isouter=True
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationid) \
			.group_by(stpl_playlistFk) \
			.order_by(
				desc(func.max(coalesce(uah_queuedTimestamp), 0)),
				desc(func.max(coalesce(uah_timestamp), 0)),
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


	def get_random_playlistIds(
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
			(weigh(a) for a in ages),
			start=1.0
		)
		weights = [weigh(a)/total for a in ages]
		zeroCount = sum(1 for w in weights if w == 0)
		sampleSize = deficitSize if deficitSize < len(rows) - zeroCount \
			else len(rows) - zeroCount
		ids = [r[0] for r in rows]
		if not ids:
			raise RuntimeError("No playlist possibilities were found")
		selection = self.choice(ids, sampleSize, weights)
		return selection


	def queue_count(
		self,
		stationId: int,
	) -> int:
		query = select(func.count(distinct(q_parentKey)))\
				.select_from(station_queue)\
				.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.join(playlists_songs_tbl, sg_pk == plsg_songFk)\
				.where(q_itemType == StationRequestTypes.PLAYLIST.lower())\
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
		playlistIds = self.get_random_playlistIds(stationId, deficitSize)
		songPlaylistQuery = select(sg_pk, plsg_playlistFk, plsg_lexorder)\
			.join(playlists_songs_tbl,sg_pk == plsg_songFk)\
			.where(plsg_playlistFk.in_(playlistIds))\
			.where(sg_deletedTimstamp.is_(None))
		
		songTuples = self.conn.execute(songPlaylistQuery).fetchall()
		sortMap = {p[1]:p[0] for p in enumerate(playlistIds)}
		sortedSongs = sorted(
			(r for r in songTuples),
			key=lambda r: (sortMap[r[1]], r[2] or b"")
		)
		self.queue_service.queue_insert_songs(
			[QueueRequest(
				id=r[0],
				itemtype=StationRequestTypes.PLAYLIST.lower(),
				parentKey=r[1]
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
			self.can_playlist_be_queued_to_station(
				itemId,
				station.id
			):
			query = select(sg_pk)\
				.join(playlists_songs_tbl, sg_pk == plsg_songFk)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(plsg_playlistFk == itemId)

			rows = self.conn.execute(query)
			self.queue_service.queue_insert_songs(
				[QueueRequest(
					id=r[0],
					itemtype=StationRequestTypes.PLAYLIST.lower(),
					parentKey=itemId
				) for r in rows],
				station.id,
			)
			self.conn.commit()
			return
		raise LookupError(f"album cannot be added to {station.name}")


	def can_playlist_be_queued_to_station(
		self,
		playlistId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_playlists_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(stab_stationFk == stationId)\
			.where(or_(
				st_typeid == StationTypes.PLAYLISTS_ONLY.value,
				st_typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value
			))\
			.where(stpl_playlistFk == playlistId)
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

		#we may have to store playlist name in album
		playlistOffset = len({(l.parentkey, l.itemtype) for l in loaded})\
			if loaded else 0

		if self.is_queue_empty(stationId, playlistOffset):
			self.fil_up_queue(stationId, self.queue_size + 1 - playlistOffset)
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
		queryParams: SimpleQueryParameters,
		name: str = "",
		parentname: str = "",
		creator: str = "",
	) -> Tuple[list[CatalogueItem], int]:
		offset = queryParams.page * queryParams.limit if queryParams.limit else 0
		lcollection = clean_search_term_for_like(name)
		lcreator = clean_search_term_for_like(creator)

		query = select(
			pl_pk.label("id"),
			pl_name.label("name"),
			u_displayName.label("creator"),
			pl_ownerFk.label("ownerid"),
			u_pk,
			u_username,
		)\
			.select_from(stations_tbl) \
			.join(stations_playlists_tbl, st_pk == stpl_stationFk) \
			.join(playlists_tbl, stpl_playlistFk == pl_pk) \
			.join(users_tbl, pl_ownerFk == u_pk)\
			.where(st_pk == stationId)
		
		if lcollection:
			query = query.where(pl_name.like(f"%{lcollection}%"))

		if lcreator:
			query = query.where(u_displayName.like(f"%{lcreator}%"))

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
			itemtype="Playlist",
			requesttypeid=StationTypes.PLAYLISTS_ONLY.value,
			queuedtimestamp=0,
			rules=[] if userId and r[u_pk] != userId else [
				ActionRule(
					domain=UserRoleDomain.Playlist.value,
					name=UserRoleDef.PLAYLIST_EDIT.value,
					priority=RulePriorityLevel.OWNER.value
				)
			],
			owner=OwnerInfo(
				id=r[u_pk],
				username=r[u_username],
				displayname=r["ownerid"]
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
		return { StationRequestTypes.PLAYLIST }