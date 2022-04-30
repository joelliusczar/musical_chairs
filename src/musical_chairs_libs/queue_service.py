import time
from typing import Any, Callable, List, Optional, Tuple, Iterator
from collections.abc import Iterable
from sqlalchemy import select, desc, func, insert, delete, update
from sqlalchemy.engine.row import Row
from sqlalchemy.sql import ColumnCollection
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection
from musical_chairs_libs.tables import stations_history, songs, stations,\
	stations_tags, songs_tags, station_queue, albums, artists, song_artist
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.dtos import QueueItem, CurrentPlayingInfo
from numpy.random import choice as numpy_choice #type: ignore

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
		conn: Optional[WrappedDbConnection] = None, 
		stationService: Optional[StationService]=None,
		historyService: Optional[HistoryService]=None,
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
			if not choiceSelector:
				choiceSelector = choice
			self.conn = conn
			self.station_service = stationService
			self.history_service = historyService
			self.choice = choiceSelector

	def get_all_station_song_possibilities(self, stationPk: int) -> List[Row]:
		st: ColumnCollection = stations.columns
		sg: ColumnCollection = songs.columns
		sttg: ColumnCollection = stations_tags.columns
		sgtg: ColumnCollection = songs_tags.columns
		hist: ColumnCollection = stations_history.columns
		
		query = select(sg.pk, sg.path) \
			.select_from(stations) \
			.join(stations_tags, st.pk == sttg.stationFk) \
			.join(songs_tags, sgtg.tagFk == sttg.tagFk) \
			.join(songs, sg.pk == sgtg.songFk) \
			.join(stations_history, (hist.stationFk == st.pk) \
				& (hist.songFk == sg.pk), isouter=True) \
			.where(st.pk == stationPk) \
			.where((sgtg.skip == None) | (sgtg.skip == 0)) \
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
		songPks: List[int] = list(map(lambda r: r.pk, rows)) #type: ignore
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
		timestamp = time.time()
		params = list(map(lambda s: {
			"stationFk": stationPk, 
			"songFk": s, 
			"queuedTimestamp": timestamp 
		}, songPks))
		queueInsert = insert(station_queue)
		self.conn.execute(queueInsert, params)
		historyInsert = insert(stations_history)
		self.conn.execute(historyInsert, params)

	def move_from_queue_to_history(
		self, 
		stationPk: int, 
		songPk: int, 
		queueTimestamp: float
	) -> None:
		q = station_queue.c
		# can't delete by songPk alone b/c the song might be queued multiple times
		queueDel = delete(station_queue).where(q.stationFk == stationPk) \
			.where(q.songFk == songPk) \
			.where(q.queuedTimestamp == queueTimestamp)
		self.conn.execute(queueDel)
		currentTime = time.time()

		hist: ColumnCollection = stations_history.columns

		histUpdateStmt = update(stations_history) \
			.values(playedTimestamp = currentTime) \
			.where(hist.stationFk == stationPk) \
			.where(hist.songFk == songPk) \
			.where(hist.queuedTimestamp == queueTimestamp)
		self.conn.execute(histUpdateStmt)



	def is_queue_empty(self, stationPk: int) -> bool:
		q: ColumnCollection = station_queue.columns
		query = select(func.count(1)).select_from(station_queue)\
			.where(q.stationFk == stationPk)
		countRes = self.conn.execute(query).scalar()
		res = countRes if countRes else 0
		return res < 1

	def get_queue_for_station(
		self, 
		stationPk: Optional[int]=None, 
		stationName: Optional[str]=None,
		limit: Optional[int]=None
	) -> Iterator[QueueItem]:
		sg: ColumnCollection = songs.columns
		q: ColumnCollection = station_queue.columns
		ab: ColumnCollection = albums.columns
		ar: ColumnCollection = artists.columns
		sgar: ColumnCollection = song_artist.columns
		st: ColumnCollection = stations.columns
		baseQuery = select(
				sg.pk, \
				sg.path, \
				sg.name, \
				ab.name.label("album"), \
				ar.name.label("artist"), \
				q.queuedTimestamp
			).select_from(station_queue) \
			.join(songs, sg.pk == q.songFk) \
			.join(albums, sg.albumFk == ab.pk, isouter=True) \
			.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
			.join(artists, sgar.artistFk == ar.pk, isouter=True) \
			.order_by(q.queuedTimestamp)
		if stationPk:
			query = baseQuery.where(q.stationFk == stationPk)
		elif stationName:
			query = baseQuery.join(stations, st.pk == q.stationFk) \
				.where(st.name == stationName)
		else:
			raise ValueError("Either stationName or pk must be provided")
		records = self.conn.execute(query)
		for row in records: 
			yield QueueItem(
				row.pk, 
				row.name, 
				row.album, 
				row.artist, 
				row.path, 
				row.queuedTimestamp 
			)

	def pop_next_queued(
		self, 
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None, 
		queueSize: int=50
	) -> Tuple[str, str, str, str]:
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_pk(stationName)
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
		return (queueItem.path, queueItem.name, queueItem.album, queueItem.artist)

	def add_song_to_queue(
		self, 
		songPk: int,
		stationPk: Optional[int]=None, 
		stationName: Optional[str]=None
	) -> int:
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_pk(stationName)
		timestamp = time.time()
		sq: ColumnCollection = station_queue.columns
		st: ColumnCollection = stations.columns
		sttg: ColumnCollection = stations_tags.columns
		sgtg: ColumnCollection = songs_tags.columns

		subquery = select(st.pk) \
			.select_from(stations) \
			.join(stations_tags, sttg.stationFk == st.pk) \
			.join(songs_tags, sgtg.tagFk == sttg.tagFk) \
			.where(sgtg.songFk == songPk)
		baseFromQuery= select(
				st.pk, \
				literal(songPk), \
				literal(timestamp), \
				literal(timestamp)) \
					.where(st.pk.in_(subquery))
		if stationPk:
			fromQuery = baseFromQuery.where(st.stationFk == stationPk)
		elif stationName:
			fromQuery = baseFromQuery.where(st.name == stationName) \
				.where(st.name == stationName)
		else:
				raise ValueError("Either stationName or pk must be provided")
		stmt = insert(station_queue).from_select(
			[
				sq.stationFk, \
				sq.songFk, \
				sq.addedTimestamp, \
				sq.requestedTimestamp \
			], \
			fromQuery
		)
		return self.conn.execute(stmt).rowcount #type: ignore
	

	def get_now_playing_and_queue(
		self, 
		stationPk: Optional[int]=None, 
		stationName: Optional[str]=None
	) -> CurrentPlayingInfo:
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_pk(stationName)
			else:
				raise ValueError("Either stationName or pk must be provided")
		queue = list(self.get_queue_for_station(stationPk))
		playing = next(self.history_service. \
			get_history_for_station(stationPk, limit=1), None)
		return CurrentPlayingInfo(playing, queue)




if __name__ == "__main__":
	pass