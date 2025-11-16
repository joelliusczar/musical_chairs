from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	AlbumListDisplayItem,
	clean_search_term_for_like,
	get_datetime,
	SongListDisplayItem,
	StationInfo,
	UserRoleDef,
	TrackingInfo,
)
from musical_chairs_libs.dtos_and_utilities.constants import StationTypes
from .queue_service import QueueService
from musical_chairs_libs.tables import (
	albums as albums_tbl, ab_pk, ab_name, ab_year, ab_versionnote, ab_albumArtistFk,
	artists as artists_tbl, ar_pk, ar_name,
	songs,
	stations as stations_tbl, st_typeid,
	user_action_history as user_action_history_tbl, uah_pk, uah_queuedTimestamp,
	uah_timestamp, uah_action,
	station_queue, q_userActionHistoryFk, q_songFk, q_stationFk,
	sg_disc, sg_pk, sg_albumFk, sg_deletedTimstamp,
	sg_track,
	st_pk,
	last_played, lp_songFk, lp_stationFk, lp_timestamp,
	stations_albums as stations_albums_tbl, stab_albumFk, stab_stationFk,
	stations_songs as stations_songs_tbl
)
from numpy.random import (
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]
)
from sqlalchemy import (
	select,
	func,
	update,
)
from sqlalchemy.engine import Connection
from typing import (
	Any,
	Callable,
	Optional,
	cast,
	Collection,
	Sequence,
	Set,
	Tuple,
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

class AlbumQueueService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		queueService: Optional[QueueService]=None,
		choiceSelector: Optional[
			Callable[[Sequence[Any], int], Collection[Any]]
		]=None,
	) -> None:
			if not conn:
				raise RuntimeError("No connection provided")
			if not queueService:
				queueService = QueueService(conn)
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.queue_service = queueService
			self.choice = choiceSelector
			self.get_datetime = get_datetime
			self.queue_size = 50
			self.album_queue_size = 3

	def __get_album_played_timestamps__(self, stationid: int) -> dict[int, float]:

		query = select(
			sg_albumFk,
			func.max(uah_queuedTimestamp),
			func.max(uah_timestamp),
			func.max(lp_timestamp)
		)\
			.select_from(songs)\
			.join(stations_albums_tbl, stab_albumFk == sg_albumFk)\
			.join(stations_tbl, st_pk == stab_stationFk)\
			.join(
				station_queue,
				q_songFk == sg_pk & q_stationFk == st_pk,
				isouter=True
			)\
			.join(last_played, (lp_stationFk == st_pk) \
				& (lp_songFk == sg_pk), isouter=True
			)\
			.join(user_action_history_tbl,
				(uah_pk == q_userActionHistoryFk) & uah_timestamp.isnot(None),
				isouter=True
			)\
			.where(sg_deletedTimstamp.is_(None))\
			.where(st_pk == stationid)\
			.where(st_typeid == StationTypes.ALBUMS_ONLY.value)\
			.group_by(sg_albumFk)
		
		rows = self.conn.execute(query)
		return {
			cast(int,r[0]):cast(float,max(r[1] or 0, r[2] or 0, r[3] or 0)) 
			for r in rows
		}

	def get_all_station_album_possibilities(
		self,
		stationid: int
	) -> Sequence[int]:
		query = select(stab_albumFk)\
			.where(stab_stationFk == stationid)
		rows = self.conn.execute(query).fetchall()
		lastPlayedMap = self.__get_album_played_timestamps__(stationid)
		return sorted(
			(cast(int,r[0]) for r in rows),
			key=lambda aid: lastPlayedMap[aid]
		)

	def get_random_albumIds(
		self,
		stationid: int,
		deficitSize: int
	) -> Collection[int]:
		ids = self.get_all_station_album_possibilities(stationid)
		sampleSize = deficitSize if deficitSize < len(ids) else len(ids)
		if not ids:
			raise RuntimeError("No album possibilities were found")
		selection = self.choice(ids, sampleSize)
		return selection

	def fil_up_album_queue(self, stationId: int, queueSize: int) -> None:
		
		count = self.queue_service.queue_count(stationId, StationTypes.ALBUMS_ONLY)

		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		albumIds = self.get_random_albumIds(stationId, deficitSize)
		songAlbumQuery = select(sg_pk, sg_albumFk)\
			.where(sg_albumFk.in_(albumIds))\
			.where(sg_deletedTimstamp.is_(None))\
			.order_by(
				sg_disc,
				sg_track
			)
		songTuples = self.conn.execute(songAlbumQuery).fetchall()
		self.queue_service.queue_insert_songs(
			[r[0] for r in songTuples],
			stationId
		)

	def add_album_to_queue(
		self,
		albumId: int,
		station: StationInfo,
		user: AccountInfo,
		trackingInfo: TrackingInfo
	):
		if station and\
			self.can_album_be_queued_to_station(
				albumId,
				station.id
			):
			query = select(sg_pk)\
				.where(sg_deletedTimstamp.is_(None))\
				.where(sg_albumFk == albumId)
			rows = self.conn.execute(query)
			self.queue_service.queue_insert_songs(
				[r[0] for r in rows],
				station.id,
				user.id,
				trackingInfo
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
			.where(st_typeid == StationTypes.ALBUMS_ONLY.value)\
			.where(stab_albumFk == albumId)\
			.where(stab_stationFk == stationId)
		countRes = self.conn.execute(query).scalar()
		return True if countRes and countRes > 0 else False

	def queue_count(
		self,
		stationId: Optional[int]=None
	) -> int:
		query = select(func.count(1))
		query = query.select_from(station_queue)\
				.join(user_action_history_tbl, uah_pk == q_userActionHistoryFk)\
				.join(songs, sg_pk == q_songFk)
		if stationId:
			query = query.where(q_stationFk == stationId)
		else:
			raise ValueError("Either stationName or id must be provided")
		query = query\
			.where(sg_deletedTimstamp.is_(None))\
			.where(uah_timestamp.is_(None))
		count = self.conn.execute(query).scalar() or 0
		return count

	def is_queue_empty(
		self,
		stationId: int,
		offset: int = 0,
		stationtype: StationTypes = StationTypes.SONGS_ONLY
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

		offset = len(loaded) if loaded else 0

		if self.is_queue_empty(stationId, offset):
			self.queue_service.fil_up_queue(stationId, self.queue_size + 1 - offset)
			self.conn.commit()


		results, _ = self.queue_service.get_queue_for_station(
			stationId,
			limit=self.queue_size
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
		self.fil_up_album_queue(stationId, self.album_queue_size)
		self.conn.commit()
		return updCount > 0
	
	def get_album_catalogue(
		self,
		stationId: int,
		page: int = 0,
		album: str = "",
		artist: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[AlbumListDisplayItem], int]:
		offset = page * limit if limit else 0
		lalbum = clean_search_term_for_like(album)
		lartist = clean_search_term_for_like(artist)

		query = select(
			ab_pk.label("id"),
			ab_name.label("name"),
			ar_name.label("albumartist"),
			ab_year.label("year"),
			ab_versionnote.label("versionnote")
		)\
			.select_from(stations_tbl) \
			.join(stations_songs_tbl, st_pk == stab_stationFk) \
			.join(albums_tbl, stab_albumFk == ab_pk) \
			.join(artists_tbl, ab_albumArtistFk == ar_pk, isouter=True) \
			.where(st_pk == stationId)
		
		if lalbum:
			query = query.where(ab_name.like(f"%{lalbum}%"))

		if lartist:
			query = query.where(ar_name.like(f"%{lartist}%"))

		limitedQuery = query\
			.offset(offset)\
			.limit(limit)

		records = self.conn.execute(limitedQuery).mappings()

		result = [AlbumListDisplayItem(**r) for r in records]
		countQuery = select(func.count(1))\
			.select_from(cast(Any, query))
		count = self.conn.execute(countQuery).scalar() or 0
		return result, count