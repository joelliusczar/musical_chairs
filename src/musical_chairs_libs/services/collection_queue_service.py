from collections import defaultdict
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
	StationTypes,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationRequestTypes,
)
from musical_chairs_libs.protocols import SongPopper, RadioPusher
from musical_chairs_libs.tables import (
	albums as albums_tbl, ab_pk, ab_name, ab_year, ab_albumArtistFk, ab_ownerFk,
	artists as artists_tbl, ar_pk, ar_name,
	songs,
	stations as stations_tbl, st_typeid,
	user_action_history as user_action_history_tbl, uah_pk, uah_queuedTimestamp,
	uah_timestamp, uah_action,
	station_queue as station_queue_tbl, q_userActionHistoryFk, q_songFk, 
	q_stationFk, q_itemType, q_parentKey,
	sg_disc, sg_pk, sg_albumFk, sg_deletedTimstamp,
	sg_trackNum,
	st_pk,
	playlists as playlists_tbl, pl_pk, pl_name, pl_ownerFk, 
	pl_lastmodifiedtimestamp,
	playlists_songs as playlists_songs_tbl, plsg_playlistFk, plsg_songFk,
	plsg_lexorder,
	stations_albums as stations_albums_tbl, stab_albumFk, stab_stationFk,
	stations_playlists as stations_playlists_tbl, stpl_playlistFk, stpl_stationFk,
	users as users_tbl, u_pk, u_username, u_displayName,
	last_played as last_played_tbl, lp_timestamp, lp_stationFk, lp_itemType,
	lp_parentKey,
)
from .current_user_provider import CurrentUserProvider
from .queue_service import QueueService
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)
from sqlalchemy import (
	desc,
	select,
	literal as dbLiteral,
	func,
	update,
	distinct,
	union_all,
)
from sqlalchemy.engine import Connection
from sqlalchemy.sql.functions import coalesce
from typing import (
	Any,
	Callable,
	Iterator,
	Optional,
	cast,
	Collection,
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


class CollectionQueueService(SongPopper, RadioPusher):

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



	def get_all_station_possibilities(
		self,
		stationid: int
	) -> Sequence[Tuple[int, str, float]]:
		
		albumQuery = select(
			stab_albumFk.label("key"),
			func.max(coalesce(uah_queuedTimestamp,0)).label("queuedtimestamp"),
			func.max(coalesce(uah_timestamp,0)).label("timestamp"),
			func.max(coalesce(lp_timestamp,0)).label("lastplayed"),
			dbLiteral(StationRequestTypes.ALBUM.lower()).label("itemtype")
		) \
			.select_from(stations_tbl) \
			.join(stations_albums_tbl, st_pk == stab_stationFk) \
			.join(songs, sg_albumFk == stab_albumFk) \
			.join(station_queue_tbl, (q_stationFk == st_pk) \
				& (q_parentKey == stab_albumFk) \
				& (q_itemType == StationRequestTypes.ALBUM.lower()), isouter=True) \
			.join(last_played_tbl, (lp_stationFk == st_pk) \
				& (lp_parentKey == stab_albumFk)
				& (lp_itemType == StationRequestTypes.ALBUM.lower()), isouter=True
			)\
			.join(user_action_history_tbl,
				(uah_pk == q_userActionHistoryFk),
				isouter=True
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationid) \
			.group_by(stab_albumFk)
		
		playlistQuery = select(
			stpl_playlistFk.label("key"),
			func.max(coalesce(uah_queuedTimestamp,0)).label("queuedtimestamp"),
			func.max(coalesce(uah_timestamp,0)).label("timestamp"),
			func.max(coalesce(lp_timestamp,0)).label("lastplayed"),
			dbLiteral(StationRequestTypes.PLAYLIST.lower()).label("itemtype")
		) \
			.select_from(stations_tbl) \
			.join(stations_playlists_tbl, st_pk == stpl_stationFk) \
			.join(playlists_songs_tbl, plsg_playlistFk == stpl_playlistFk) \
			.join(songs, sg_pk == plsg_songFk) \
			.join(station_queue_tbl, (q_stationFk == st_pk) \
				& (q_parentKey == stpl_playlistFk) \
				& (q_itemType == StationRequestTypes.PLAYLIST.lower()), isouter=True) \
			.join(last_played_tbl, (lp_stationFk == st_pk) \
				& (lp_parentKey == stpl_playlistFk)
				& (lp_itemType == StationRequestTypes.PLAYLIST.lower()), isouter=True
			)\
			.join(user_action_history_tbl,
				(uah_pk == q_userActionHistoryFk),
				isouter=True
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationid) \
			.group_by(stpl_playlistFk)

		sub = union_all(
			albumQuery,
			playlistQuery
		).cte()

		query = select(sub.c.key, sub.c.itemtype, func.max(sub.c.queuedtimestamp))\
			.group_by(sub.c.key, sub.c.itemtype)\
			.order_by(
				desc(func.max(sub.c.queuedtimestamp)),
				desc(func.max(sub.c.timestamp)),
				desc(func.max(sub.c.lastplayed)),
				func.rand()
			)
		rows = self.conn.execute(query).fetchall()

		return [(row[0], row[1], row[2]) for row in rows]


	def get_random_collectionIds(
		self,
		stationId: int,
		deficitSize: int
	) -> Collection[Tuple[int, str]]:
		def weigh(n: float) -> float:
			return n * n
		rows = [*self.get_all_station_possibilities(stationId)]
		mostRecentDraw = rows[0][2] or self.get_datetime().timestamp() \
			if len(rows) > 1 else self.get_datetime().timestamp()
		ages = [(mostRecentDraw - r[2] or 0) for r in rows]
		total = sum(
			(weigh(a) for a in ages)
		)
		weights = [weigh(a)/total for a in ages]
		zeroCount = sum(1 for w in weights if w == 0)
		sampleSize = deficitSize if deficitSize < len(rows) - zeroCount \
			else len(rows) - zeroCount
		ids = [(r[0], r[1]) for r in rows]
		if not ids:
			raise RuntimeError("No playlist possibilities were found")
		tupleMap = {f"{t[1]}{t[0]}":t for t in ids}
		try:
			selection = self.choice(
				[f"{t[1]}{t[0]}" for t in ids],
				sampleSize,
				weights
			)
			return [tupleMap[k] for k in selection]
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
		albumQuery = select(func.count(distinct(q_parentKey)))\
				.select_from(station_queue_tbl)\
				.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.where(q_stationFk == stationId)\
				.where(q_itemType == StationRequestTypes.ALBUM.lower())\
				.where(sg_deletedTimstamp.is_(None))\
				.where(uah_timestamp.is_(None))
		
		playlistQuery = select(func.count(distinct(q_parentKey)))\
				.select_from(station_queue_tbl)\
				.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)\
				.where(q_itemType == StationRequestTypes.PLAYLIST.lower())\
				.where(q_stationFk == stationId)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(uah_timestamp.is_(None))
		albumCount = self.conn.execute(albumQuery).scalar() or 0
		playlistCount = self.conn.execute(playlistQuery).scalar() or 0
		return albumCount + playlistCount


	def fil_up_queue(self, stationId: int, queueSize: int) -> None:
		
		count = self.queue_count(stationId)

		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		collectionIds = self.get_random_collectionIds(stationId, deficitSize)

		albumIds = [
			a[0] for a in collectionIds 
			if a[1] == StationRequestTypes.ALBUM.lower()
		]
		songAlbumQuery = select(sg_pk, sg_albumFk, sg_disc, sg_trackNum)\
			.where(sg_albumFk.in_(albumIds))\
			.where(sg_deletedTimstamp.is_(None))
		albumSongTuples = self.conn.execute(songAlbumQuery).fetchall()
		albumsMap: defaultdict[int, list[Any]] = defaultdict(list)
		for row in albumSongTuples:
			albumsMap[row[1]].append(row)
		
		playlistIds = [
			a[0] for a in collectionIds 
			if a[1] == StationRequestTypes.PLAYLIST.lower()
		]
		songPlaylistQuery = select(sg_pk, plsg_playlistFk, plsg_lexorder)\
			.join(playlists_songs_tbl,sg_pk == plsg_songFk)\
			.where(plsg_playlistFk.in_(playlistIds))\
			.where(sg_deletedTimstamp.is_(None))
		playlistSongTuples = self.conn.execute(songPlaylistQuery).fetchall()
		playlistsMap: defaultdict[int, list[Any]] = defaultdict(list)
		for row in playlistSongTuples:
			playlistsMap[row[1]].append(row)

		requests: list[QueueRequest] = []
		
		def albumSortKey(r: list[Any]):
			return (r[2] or 0, r[3])
		
		def playlistSortKey(r: list[Any]):
			return r[2] or b""

		for collectionId in collectionIds:
			sortKey = albumSortKey \
				if collectionId[1] == StationRequestTypes.ALBUM.lower() \
				else playlistSortKey
			collectionMap = albumsMap \
				if collectionId[1] == StationRequestTypes.ALBUM.lower() \
				else playlistsMap
			sortedSongs = sorted(
				collectionMap[collectionId[0]],
				key=sortKey
			)
			requests.extend(
				QueueRequest(
					id=r[0],
					itemtype=collectionId[1].lower(),
					parentKey=collectionId[0]
				) for r in sortedSongs
			)


		self.queue_service.queue_insert_songs(
			requests,
			stationId
		)


	def __add_album_to_queue__(
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
	

	def __add_playlist_to_queue__(
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


	def add_to_queue(
		self,
		itemId: int,
		station: StationInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST,
	):
		
		if stationItemType == StationRequestTypes.ALBUM:
			self.__add_album_to_queue__(
				itemId,
				station,
				stationItemType
			)
		elif stationItemType == StationRequestTypes.PLAYLIST:
			self.__add_playlist_to_queue__(
				itemId,
				station,
				stationItemType
			)
		return
	

	def can_playlist_be_queued_to_station(
		self,
		playlistId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_playlists_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(stab_stationFk == stationId)\
			.where(
				st_typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value
			)\
			.where(stpl_playlistFk == playlistId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False
	

	def can_album_be_queued_to_station(
		self,
		albumId: int,
		stationId: int
	) -> bool:
		query = select(func.count(1)).select_from(stations_albums_tbl)\
			.join(stations_tbl, stab_stationFk == st_pk)\
			.where(stab_stationFk == stationId)\
			.where(
				st_typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value
			)\
			.where(stab_albumFk == albumId)
		
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	
	def can_collection_be_queued_to_station(
		self,
		collectionId: int,
		stationId: int,
		stationItemType: StationRequestTypes
	) -> bool:
		if stationItemType == StationRequestTypes.ALBUM:
			return self.can_album_be_queued_to_station(
				collectionId, 
				stationId
			)
		if stationItemType == StationRequestTypes.PLAYLIST:
			return self.can_playlist_be_queued_to_station(
				collectionId,
				stationId
			)
		return False


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
		collectionOffset = len({(l.parentkey, l.itemtype) for l in loaded})\
			if loaded else 0

		if self.is_queue_empty(stationId, collectionOffset):
			self.fil_up_queue(stationId, self.queue_size + 1 - collectionOffset)
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
			.join(station_queue_tbl, uah_pk == q_userActionHistoryFk)\
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
		lname = clean_search_term_for_like(name)
		lcreator = clean_search_term_for_like(creator)

		albumQuery = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ar_name.label("creator"),
			ab_year.label("year"),
			ab_ownerFk.label("ownerid"),
			u_username.label("ownerusername"),
			u_displayName.label("ownerdisplayname"),
			dbLiteral(StationRequestTypes.ALBUM.lower()).label("itemtype")
		)\
			.select_from(stations_tbl) \
			.join(stations_albums_tbl, st_pk == stab_stationFk) \
			.join(albums_tbl, stab_albumFk == ab_pk) \
			.join(artists_tbl, ab_albumArtistFk == ar_pk, isouter=True) \
			.join(users_tbl, u_pk == ab_ownerFk, isouter=True)\
			.where(st_pk == stationId)
		
		playlistQuery = select(
			pl_pk.label("id"),
			pl_name.label("name"),
			u_displayName.label("creator"),
			func.FROM_UNIXTIME(pl_lastmodifiedtimestamp, "%Y").label("year"),
			pl_ownerFk.label("ownerid"),
			u_username.label("ownerusername"),
			u_displayName.label("ownerdisplayname"),
			dbLiteral(StationRequestTypes.PLAYLIST.lower()).label("itemtype")
		)\
			.select_from(stations_tbl) \
			.join(stations_playlists_tbl, st_pk == stpl_stationFk) \
			.join(playlists_tbl, stpl_playlistFk == pl_pk) \
			.join(users_tbl, pl_ownerFk == u_pk)\
			.where(st_pk == stationId)
		
		unioned_query = union_all(albumQuery, playlistQuery)
		sub = unioned_query.cte()
		
		query = select(
			sub.c.id.label("id"),
			sub.c.name.label("name"),
			sub.c.creator.label("creator"),
			sub.c.year.label("year"),
			sub.c.ownerid.label("ownerid"),
			sub.c.ownerusername.label("ownerusername"),
			sub.c.ownerdisplayname.label("ownerdisplayname"),
			sub.c.itemtype.label("itemtype")
		)
		
		if lname:
			query = query.where(sub.c.name.like(f"%{lname}%"))

		if lcreator:
			query = query.where(sub.c.creator.like(f"%{lcreator}%"))

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
			itemtype=r["itemtype"],
			requesttypeid=StationRequestTypes.ALBUM.value \
				if r["itemtype"] == StationRequestTypes.ALBUM.lower() \
				else StationRequestTypes.PLAYLIST.value ,
			queuedtimestamp=0,
			rules=[] if not userId or r["ownerid"] != userId else [
				ActionRule(
					domain=UserRoleDomain.Album.value,
					name=UserRoleDef.ALBUM_EDIT.value,
					priority=RulePriorityLevel.OWNER.value
				)
			] if r["itemtype"] == StationRequestTypes.ALBUM.lower()
			else [
				ActionRule(
					domain=UserRoleDomain.Playlist.value,
					name=UserRoleDef.PLAYLIST_EDIT.value,
					priority=RulePriorityLevel.OWNER.value
				)
			],
			owner=OwnerInfo(
				id=r["ownerid"],
				username=r["ownerusername"],
				displayname=r["ownerdisplayname"]
			)
			) for r in records]
		countQuery = select(func.count(1)).select_from(sub)
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
		return { StationRequestTypes.ALBUM, StationRequestTypes.PLAYLIST }


	def get_queue_for_station(
		self,
		stationId: int
	) -> Iterator[dict[str, Any]]:
		query = select(
			q_songFk,
			q_itemType,
			q_parentKey,
			uah_queuedTimestamp,
		)\
			.select_from(station_queue_tbl)\
			.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
			.where(q_stationFk == stationId)\
			.where(uah_timestamp.is_(None))\
			.order_by(uah_queuedTimestamp)

		records = self.conn.execute(query)
		yield from (
			{
				"songId": record[0],
				"itemType": record[1], 
				"parentKey": record[2],
				"queuedTimestamp": record[3],
			}
			for record in records)




