#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import Iterator, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.sql import ColumnCollection
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import stations_history, songs, stations, \
	albums, artists, song_artist
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.dtos import HistoryItem
from musical_chairs_libs.env_manager import EnvManager




class HistoryService:
	def __init__(
		self, 
		conn: Connection, 
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
		h: ColumnCollection = stations_history.columns 
		st: ColumnCollection = stations.columns 
		sg: ColumnCollection = songs.columns 
		ab: ColumnCollection = albums.columns 
		ar: ColumnCollection = artists.columns 
		sgar: ColumnCollection = song_artist.columns 
		baseQuery = select(
			sg.pk, 
			sg.path, 
			h.playedTimestamp, 
			sg.name, 
			ab.name.label("album"),
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
				.where(func.lower(st.name) == func.lower(stationName))
		else:
			raise ValueError("Either stationName or pk must be provided")
		records = self.conn.execute(query) 
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield HistoryItem( 
					row.pk, #pyright: ignore [reportUnknownArgumentType]
					row.name, #pyright: ignore [reportUnknownArgumentType]
					row.album, #pyright: ignore [reportUnknownArgumentType]
					row.artist, #pyright: ignore [reportUnknownArgumentType]
					row.playedTimestamp #pyright: ignore [reportUnknownArgumentType]
				)