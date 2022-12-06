#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import (
	Any,
	Callable,
	List,
	Optional,
	Tuple,
	Iterator,
	cast
)
from collections.abc import Iterable
from sqlalchemy import\
	select,\
	desc,\
	func,\
	insert,\
	delete,\
	update
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from sqlalchemy.sql import ColumnCollection
from .env_manager import EnvManager
from .station_service import StationService
from .accounts_service import AccountsService
from .song_info_service import SongInfoService
from .history_service import HistoryService
from musical_chairs_libs.tables import (
	stations_history,
	songs,
	stations,
	stations_songs as stations_songs_tbl, stsg_stationFk, stsg_songFk,
	station_queue, q_songFk, q_queuedTimestamp, q_stationFk,
	albums,
	artists,
	song_artist,
	sgar_pk, sgar_songFk, sgar_artistFk, sgar_isPrimaryArtist,
	sg_pk, sg_name, sg_path, sg_albumFk,
	st_pk, st_name,
	ar_pk, ar_name,
	ab_pk, ab_name
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	QueueItem,
	CurrentPlayingInfo,
	get_datetime,
	SearchNameString
)
from numpy.random import \
	choice as numpy_choice #pyright: ignore [reportUnknownVariableType]


def choice(
	items: List[Any],
	sampleSize: int
) -> Iterable[Any]:
	aSize = len(items)
	pSize = len(items) + 1
	# the sum of weights needs to equal 1
	weights = [2 * (float(n) / (pSize * aSize)) for n in range(1, pSize)]
	return numpy_choice(items, sampleSize, p = weights, replace=False).tolist()

class QueueService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		stationService: Optional[StationService]=None,
		historyService: Optional[HistoryService]=None,
		accountService: Optional[AccountsService]=None,
		songInfoService: Optional[SongInfoService]=None,
		choiceSelector: Optional[Callable[[List[Any], int], Iterable[Any]]]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
			if not conn:
				if not envManager:
					envManager = EnvManager()
				conn = envManager.get_configured_db_connection()
			if not stationService:
				stationService = StationService(conn)
			if not historyService:
				historyService = HistoryService(conn, stationService)
			if not accountService:
				accountService = AccountsService(conn, envManager)
			if not songInfoService:
				songInfoService = SongInfoService(conn)
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.station_service = stationService
			self.history_service = historyService
			self.account_service = accountService
			self.song_info_service = songInfoService
			self.choice = choiceSelector
			self.get_datetime = get_datetime

	def get_all_station_song_possibilities(self, stationPk: int) -> List[Row]:
		st: ColumnCollection = stations.columns
		sg: ColumnCollection = songs.columns
		hist: ColumnCollection = stations_history.columns

		query = select(sg.pk, sg.path) \
			.select_from(stations) \
			.join(stations_songs_tbl, st.pk == stsg_stationFk) \
			.join(songs, sg.pk == stsg_songFk) \
			.join(stations_history, (hist.stationFk == st.pk) \
				& (hist.songFk == sg.pk), isouter=True) \
			.where(st.pk == stationPk) \
			.group_by(sg.pk, sg.path) \
			.order_by(desc(func.max(hist.queuedTimestamp))) \
			.order_by(desc(func.max(hist.playedTimestamp)))

		rows: List[Row] = self.conn.execute(query).fetchall()
		return rows

	def get_random_songPks(
		self,
		stationPk: int,
		deficitSize: int
	) -> Iterable[int]:
		rows = self.get_all_station_song_possibilities(stationPk)
		sampleSize = deficitSize if deficitSize < len(rows) else len(rows)
		songPks = [r["pk"] for r in rows]
		selection = self.choice(songPks, sampleSize)
		return selection


	def fil_up_queue(self, stationPk: int, queueSize: int) -> None:
		q: ColumnCollection = station_queue.columns
		queryQueueSize: str = select(func.count(1)).select_from(station_queue)\
			.where(q.stationFk == stationPk)
		countRes = self.conn.execute(queryQueueSize).scalar()
		count: int = countRes if countRes else 0
		deficitSize = queueSize - count
		if deficitSize < 1:
			return
		songPks = self.get_random_songPks(stationPk, deficitSize)
		timestamp = self.get_datetime().timestamp()
		params = [{
			"stationFk": stationPk,
			"songFk": s,
			"queuedTimestamp": timestamp
		} for s in songPks]
		queueInsert = insert(station_queue)
		self.conn.execute(queueInsert, params)
		historyInsert = insert(stations_history)
		self.conn.execute(historyInsert, params)

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> None:

		# can't delete by songId alone b/c the song might be queued multiple times
		self._remove_song_from_queue(
			songId,
			queueTimestamp,
			stationId,
		)
		currentTime = self.get_datetime().timestamp()

		hist: ColumnCollection = stations_history.columns

		histUpdateStmt = update(stations_history) \
			.values(playedTimestamp = currentTime) \
			.where(hist.stationFk == stationId) \
			.where(hist.songFk == songId) \
			.where(hist.queuedTimestamp == queueTimestamp)
		self.conn.execute(histUpdateStmt)



	def is_queue_empty(self, stationId: int) -> bool:
		res = self.queue_count(stationId)
		return res < 1

	def get_queue_for_station(
		self,
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None,
		limit: Optional[int]=None
	) -> Iterator[QueueItem]:
		primaryArtistGroupQuery = select(
			func.max(sgar_pk).label("pk"),
			func.max(sgar_isPrimaryArtist).label("isPrimary")
		).group_by(sgar_songFk)
		subq = primaryArtistGroupQuery.subquery()

		baseQuery = select(
				sg_pk,
				sg_path,
				sg_name,
				ab_name.label("album"),
				ar_name.label("artist"),
				q_queuedTimestamp
			).select_from(station_queue)\
				.join(songs, sg_pk == q_songFk)\
				.join(albums, sg_albumFk == ab_pk, isouter=True)\
				.join(song_artist, sg_pk == sgar_songFk, isouter=True)\
				.join(artists, sgar_artistFk == ar_pk, isouter=True)\
				.join(subq, subq.c.pk == sgar_pk)
		if stationPk:
			query = baseQuery.where(q_stationFk == stationPk)
		elif stationName:
			query = baseQuery.join(stations, st_pk == q_stationFk) \
				.where(func.lower(st_name) == func.lower(stationName))
		else:
			raise ValueError("Either stationName or pk must be provided")
		records = self.conn.execute(query.order_by(q_queuedTimestamp))
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield QueueItem(
				id=row[sg_pk], #pyright: ignore [reportUnknownArgumentType]
				name=row[sg_name], #pyright: ignore [reportUnknownArgumentType]
				album=row["album"], #pyright: ignore [reportUnknownArgumentType]
				artist=row["artist"], #pyright: ignore [reportUnknownArgumentType]
				path=row[sg_path], #pyright: ignore [reportUnknownArgumentType]
				queuedTimestamp=row[q_queuedTimestamp] #pyright: ignore [reportUnknownArgumentType]
			)

	def pop_next_queued(
		self,
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None,
		queueSize: int=50
	) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_id(stationName)
		if not stationPk:
			raise ValueError("Either stationName or pk must be provided")
		if self.is_queue_empty(stationPk):
			self.fil_up_queue(stationPk, queueSize + 1)
		results = self.get_queue_for_station(stationPk, limit=1)
		queueItem = next(results)
		self.move_from_queue_to_history(stationPk, \
			queueItem.id, \
			queueItem.queuedTimestamp)
		self.fil_up_queue(stationPk, queueSize)
		return (
			queueItem.path, \
			queueItem.name, \
			queueItem.album, \
			queueItem.artist
		)

	def _add_song_to_queue(
		self,
		songPk: int,
		stationPk: int,
		userPk: int
	) -> int:
		timestamp = self.get_datetime().timestamp()

		stmt = insert(station_queue).values(
			stationFk = stationPk,
			songFk = songPk,
			queuedTimestamp = timestamp,
			requestedTimestamp = timestamp,
			requestedByUserFk = userPk
		)
		return self.conn.execute(stmt).rowcount #pyright: ignore [reportUnknownVariableType]

	def add_song_to_queue(self,
		songId: int,
		stationName: str,
		user: AccountInfo
	):
		stationPk = self.station_service.get_station_id(stationName)
		songInfo = self.song_info_service.song_info(songId)
		songName = songInfo.name if songInfo else "Song"
		if stationPk and\
			self.station_service.can_song_be_queued_to_station(
				songId,
				stationPk
			):
			self._add_song_to_queue(songId, stationPk, user.id)
			return
		raise LookupError(f"{songName} cannot be added to {stationName}")

	def queue_count(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> int:
		query = select(func.count(1)).select_from(station_queue)
		if stationId:
			query = query.where(q_stationFk == stationId)
		elif stationName:
			query.join(stations, st_pk == q_stationFk)\
				.where(func.format_name_for_search(st_name)
					== SearchNameString.format_name_for_search(stationName))
		else:
			raise ValueError("Either stationName or id must be provided")

		count = self.conn.execute(query).scalar() or 0
		return count


	def get_now_playing_and_queue(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> CurrentPlayingInfo:
		if not stationId:
			if stationName:
				stationId = self.station_service.get_station_id(stationName)
			else:
				raise ValueError("Either stationName or id must be provided")
		queue = list(self.get_queue_for_station(stationId))
		playing = next(self.history_service. \
			get_history_for_station(stationId, limit=1), None)
		return CurrentPlayingInfo(
			nowPlaying=playing,
			items=queue,
			totalRows=self.queue_count(stationId, stationName)
		)

	def _remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> bool:
		stmt = delete(station_queue)

		if stationId:
			stmt = stmt.where(q_stationFk == stationId)
		elif stationName:
			subQ = select(st_pk).where(func.format_name_for_search(st_name)
				== SearchNameString.format_name_for_search(stationName)).\
					subquery()
			stmt = stmt.where(q_stationFk.in_(subQ))
		else:
			raise ValueError("Either stationName or id must be provided")

		stmt = stmt.where(q_songFk == songId)\
			.where(q_queuedTimestamp == queuedTimestamp)
		return cast(int, self.conn.execute(stmt).rowcount) > 0

	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None,
	) -> Optional[CurrentPlayingInfo]:
		if not self._remove_song_from_queue(
			songId,
			queuedTimestamp,
			stationId,
			stationName
		):
			return None
		return self.get_now_playing_and_queue(stationId, stationName)


if __name__ == "__main__":
	pass