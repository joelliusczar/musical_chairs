from collections.abc import Iterable
from sqlalchemy import select, desc
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import stations_history, songs, stations, \
	albums, artists, song_artist
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.dataclasses import HistoryItem
from musical_chairs_libs.config_loader import ConfigLoader

class HistoryService:

	def __init__(
		self, 
		conn: Connection, 
		stationService: StationService = None,
		configLoader: ConfigLoader = None
	) -> None:
			if not conn:
				if not configLoader:
					configLoader = ConfigLoader()
				conn = configLoader.get_configured_db_connection()
			if not stationService:
				stationService = StationService(conn)
			self.conn = conn
			self.station_service = stationService

	def get_history_for_station(
		self, 
		stationPk: int=None,
		stationName: str=None, 
		limit: int=50, 
		offset: int=0
	) -> Iterable[HistoryItem]:
		if not stationPk and not stationName:
			raise ValueError("Either stationName or pk must be provided")
		h = stations_history.c
		st = stations.c
		sg = songs.c
		ab = albums.c
		ar = artists.c
		sgar = song_artist.c
		baseQuery = select(
			sg.pk, \
			sg.path, \
			h.playedTimestamp, \
			sg.title, \
			ab.name.label("album"),\
			ar.name.label("artist")
		).select_from(stations_history) \
			.join(songs, h.songFk == sg.pk) \
			.join(albums, sg.albumFk == ab.pk, isouter=True) \
			.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
			.join(artists, sgar.artistFk == ar.pk, isouter=True) \
			.order_by(desc(h.playedTimestamp)) \
			.offset(offset) \
			.limit(limit)
		if stationPk:
			query = baseQuery.where(h.stationFk == stationPk)
		elif stationName:
			query = baseQuery.join(stations, st.pk == h.stationFk) \
				.where(st.name == stationName)
		records = self.conn.execute(query)
		for row in records:
			yield HistoryItem( 
					row.pk,
					row.title, 
					row.album,
					row.artist,
					row.playedTimestamp
				)