from typing import Iterator, Optional
from sqlalchemy import select, desc
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection
from musical_chairs_libs.tables import stations_history, songs, stations, \
	albums, artists, song_artist
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.dtos import HistoryItem
from musical_chairs_libs.env_manager import EnvManager



class HistoryService:
	def __init__(
		self, 
		conn: WrappedDbConnection, 
		stationService: Optional[StationService]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
			if not conn:
				if not envManager:
					envManager = EnvManager()
				conn = envManager.get_configured_db_connection()
			if not stationService:
				stationService = StationService(conn)
			self.conn = conn
			self.station_service = stationService

	def get_history_for_station(
		self, 
		stationPk: Optional[int]=None,
		stationName: Optional[str]=None, 
		limit: int=50, 
		offset: int=0
	) -> Iterator[HistoryItem]:

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
			sg.name, \
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
			query  = baseQuery.where(h.stationFk == stationPk)
		elif stationName:
			query = baseQuery.join(stations, st.pk == h.stationFk) \
				.where(st.name == stationName)
		else:
			raise ValueError("Either stationName or pk must be provided")
		records = self.conn.execute(query) 
		for row in records: #	type: ignore
			yield HistoryItem( 
					row.pk, #	type: ignore
					row.name, #	type: ignore
					row.album, #	type: ignore
					row.artist, #	type: ignore
					row.playedTimestamp #	type: ignore
				)