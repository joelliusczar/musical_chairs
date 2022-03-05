from importlib.resources import path
import time
from typing import Tuple
from collections.abc import Iterable
from musical_chairs_libs.station_service import StationService
from numpy.random import choice
from sqlalchemy import select, desc, func, insert, delete, update, literal
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import stations_history, songs, stations,\
	stations_tags, songs_tags, station_queue, albums, artists, song_artist
from musical_chairs_libs.history_service import HistoryService, HistoryItem
from musical_chairs_libs.dataclasses import QueueItem, CurrentPlayingInfo


class QueueService:

	def __init__(
		self, 
		conn: Connection, 
		stationService: StationService,
		historyService: HistoryService
	) -> None:
			self.conn: Connection = conn
			self.station_service: StationService = stationService
			self.history_service: HistoryService = historyService

	def get_all_station_song_possibilities(self, stationPk: int):
		st = stations.c
		sg = songs.c
		sttg = stations_tags.c
		sgtg = songs_tags.c
		hist = stations_history.c
		
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
		
		rows = self.conn.execute(query).fetchall()
		return rows

	def get_random_songPks(
		self, 
		stationPk: int, 
		deficitSize: int
	) -> Iterable[int]:
		rows = self.get_all_station_song_possibilities(stationPk)
		sampleSize = deficitSize if deficitSize < len(rows) else len(rows)
		aSize = len(rows)
		pSize = len(rows) + 1
		songPks = list(map(lambda r: r.pk, rows))
		# the sum of weights needs to equal 1
		weights = [2 * (float(n) / (pSize * aSize)) for n in range(1, pSize)]
		selection = choice(songPks, sampleSize, p = weights, replace=False).tolist()
		return selection

	def fil_up_queue(self, stationPk: int, queueSize: int) -> None:
		q = station_queue.c
		queryQueueSize = select(func.count(1)).select_from(station_queue)\
			.where(q.stationFk == stationPk)
		count = self.conn.execute(queryQueueSize).scalar()
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

		hist = stations_history.c

		histUpdateStmt = update(stations_history) \
			.values(playedTimestamp = currentTime) \
			.where(hist.stationFk == stationPk) \
			.where(hist.songFk == songPk) \
			.where(hist.queuedTimestamp == queueTimestamp)
		self.conn.execute(histUpdateStmt)



	def is_queue_empty(self, stationPk: int) -> bool:
		q = station_queue.c
		query = select(func.count(1)).select_from(station_queue)\
			.where(q.stationFk == stationPk)
		res = self.conn.execute(query).scalar()
		return res < 1

	def get_queue_for_station(
		self, 
		stationPk: int=None, 
		stationName: str=None,
		limit: int=None
	) -> Iterable[QueueItem]:
		if not stationPk and not stationName:
			raise ValueError("Either stationName or pk must be provided")
		sg = songs.c
		q = station_queue.c
		ab = albums.c
		ar = artists.c
		sgar = song_artist.c
		st = stations.c
		baseQuery = select(
				sg.pk, \
				sg.path, \
				sg.title, \
				ab.name.label("album"), \
				ar.name.label("artist"), \
				q.queuedTimestamp
			).select_from(station_queue) \
			.join(songs, sg.pk == q.songFk) \
			.join(albums, sg.albumFk == ab.pk, isouter=True) \
			.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
			.join(artists, sgar.artistFk == ar.pk, isouter=True) \
			.where(q.stationFk == stationPk) \
			.order_by(q.queuedTimestamp)
		if stationPk:
			query = baseQuery.where(q.stationFk == stationPk)
		elif stationName:
			query = baseQuery.join(stations, st.pk == q.stationFk) \
				.where(st.name == stationName)
		records = self.conn.execute(query)
		for row in records:
			yield QueueItem(row.pk, 
				row.path,
				row.title,
				row.album,
				row.artist,
				row.queuedTimestamp
			)

	def pop_next_queued(
		self, 
		stationPk: int=None,
		stationName: str=None, 
		queueSize: int=50
	) -> Tuple[str, str, str, str]:
		if not stationPk and not stationName:
			raise ValueError("Either stationName or pk must be provided")
		if self.is_queue_empty(stationPk):
			self.fil_up_queue(stationPk, queueSize + 1)
		results = self.get_queue_for_station(stationPk, limit=1)
		queueItem = next(results)
		self.move_from_queue_to_history(stationPk, \
			queueItem.songPk, \
			queueItem.queuedTimestamp)
		self.fil_up_queue(stationPk, queueSize)
		return (queueItem.path, queueItem.title, queueItem.album, queueItem.artist)

	def add_song_to_queue(
		self, 
		songPk: int,
		stationPk: int=None, 
		stationName: str=None
	) -> int:
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_pk(stationName)
			else:
				raise ValueError("Either stationName or pk must be provided")
		timestamp = time.time()
		sq = station_queue.c
		st = stations.c
		sttg = stations_tags.c
		sgtg = songs_tags.c

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
		stmt = insert(station_queue).from_select(
			[
				sq.stationFk, \
				sq.songFk, \
				sq.addedTimestamp, \
				sq.requestedTimestamp \
			], \
			fromQuery
			)
		rc = self.conn.execute(stmt)
		return rc.rowcount
	

	def get_now_playing_and_queue(
		self, 
		stationPk: int = None, 
		stationName: str = None
	) -> CurrentPlayingInfo:
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_pk(stationName)
			else:
				raise ValueError("Either stationName or pk must be provided")
		queue = list(self.get_queue_for_station(stationPk))
		playing = next(self.history_service\
			.get_history_for_station(stationPk, limit=1), None)
		return CurrentPlayingInfo(playing, queue)




if __name__ == "__main__":
	pass