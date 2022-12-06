#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
from typing import Iterator, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import (
	stations_history as stations_history_tbl, h_songFk, h_queuedTimestamp,
	h_stationFk,
	songs, sg_pk, sg_name, sg_albumFk,
	stations, st_name, st_pk,
	albums, ab_pk, ab_name,
	artists, ar_pk, ar_name,
	song_artist, sgar_songFk, sgar_artistFk
)
from .station_service import StationService
from .env_manager import EnvManager
from musical_chairs_libs.dtos_and_utilities import (
	HistoryItem,
	SearchNameString
)

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
		baseQuery = select(
			sg_pk.label("id"),
			h_queuedTimestamp.label("playedTimestamp"),
			sg_name.label("name"),
			ab_name.label("album"),
			ar_name.label("artist")
		).select_from(stations_history_tbl) \
			.join(songs, h_songFk == sg_pk) \
			.join(albums, sg_albumFk == ab_pk, isouter=True) \
			.join(song_artist, sg_pk == sgar_songFk, isouter=True) \
			.join(artists, sgar_artistFk == ar_pk, isouter=True) \
			.order_by(desc(h_queuedTimestamp)) \
			.offset(offset) \
			.limit(limit)
		if stationPk:
			query  = baseQuery.where(h_stationFk == stationPk)
		elif stationName:
			query = baseQuery.join(stations, st_pk == h_stationFk) \
				.where(func.lower(st_name) == func.lower(stationName))
		else:
			raise ValueError("Either stationName or pk must be provided")
		records = self.conn.execute(query)
		for row in records: #pyright: ignore [reportUnknownVariableType]
			yield HistoryItem(**row) #pyright: ignore [reportUnknownArgumentType]

	def history_count(
		self,
		stationId: Optional[int]=None,
		stationName: Optional[str]=None
	) -> int:
		query = select(func.count(1)).select_from(stations_history_tbl)
		if stationId:
			query = query.where(h_stationFk == stationId)
		elif stationName:
			query.join(stations, st_pk == h_stationFk)\
				.where(func.format_name_for_search(st_name)
					== SearchNameString.format_name_for_search(stationName))
		else:
			raise ValueError("Either stationName or id must be provided")

		count = self.conn.execute(query).scalar() or 0
		return count