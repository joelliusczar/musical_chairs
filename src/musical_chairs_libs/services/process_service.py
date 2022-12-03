import os
import platform
import subprocess
import random
from typing import Optional, Iterable, Sequence, cast
from musical_chairs_libs.dtos_and_utilities import check_name_safety,\
	SearchNameString,\
	StationInfo
from sqlalchemy import select,\
	func,\
	update
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import\
	stations as stations_tbl, st_pk, st_name, st_procId
from .env_manager import EnvManager
from .station_service import StationService

class ProcessService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None,
		stationService: Optional[StationService]=None,
		noop_mode: bool=False
	) -> None:
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		if not stationService:
				stationService = StationService(conn)
		if platform.system() == "Darwin":
			noop_mode = True
		self.noop_mode = noop_mode
		self.conn = conn
		self.station_service = stationService

	def get_pid(self) -> int:
		if self.noop_mode:
			return random.randint(0, 1000)
		return os.getpid()

	def end_process(self, procId: int) -> None:
		if self.noop_mode:
			return
		try:
			os.kill(procId, 15)
		except:
			pass

	def set_station_proc(self, stationName: str) -> None:
		pid = self.get_pid()
		stmt = update(stations_tbl)\
			.values(procId = pid) \
				.where(
					func.format_name_for_search(st_name) ==\
					str(SearchNameString.format_name_for_search(stationName))
				)
		self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def unset_station_procs(
		self,
		procIds: Optional[Iterable[int]]=None,
		stationIds: Optional[Iterable[int]]=None,
		stationNames: Optional[Sequence[str]]=None,
		stationName: Optional[str]=None
	) -> None:
		stmt = update(stations_tbl)\
			.values(procId = None)

		if isinstance(procIds, Iterable):
			stmt = stmt.where(st_procId.in_(procIds))
		elif isinstance(stationIds, Iterable):
			stmt = stmt.where(st_pk.in_(stationIds))
		elif isinstance(stationNames, Iterable):
			stmt = stmt\
				.where(func.format_name_for_search(st_name).in_(
						str(SearchNameString.format_name_for_search(s)) for s
						in stationNames
					))
		elif stationName:
			stmt = stmt\
				.where(
					func.format_name_for_search(st_name) ==\
					str(SearchNameString.format_name_for_search(stationName))
				)
		else:
			raise ValueError("procIds, stationIds, or stationNames must be provided.")
		self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def enable_stations(self,
		stationIds: Optional[Iterable[int]],
		stationNames: Optional[Sequence[str]]
	) -> None:
		stations: list[StationInfo] = []
		if stationNames and len(stationNames) == 1 and stationNames[0] == "*":
			stations = list(self.station_service.get_stations())
		else:
			stations = list(self.station_service.get_stations(
				stationIds=stationIds,
				stationNames=stationNames
			))
		for station in stations:
			self._start_station_external_process(station.name)

	def disable_stations(
		self,
		stationIds: Optional[Iterable[int]],
		stationNames: Optional[Sequence[str]]=None
	) -> None:
		query = select(st_procId).where(st_procId.is_not(None))
		if isinstance(stationIds, Iterable):
			query = query.where(st_pk.in_(stationIds))
		elif isinstance(stationNames, Iterable):
			if len(stationNames) > 1 or stationNames[0] != "*":
				query = query\
					.where(func.format_name_for_search(st_name).in_(
							str(SearchNameString.format_name_for_search(s)) for s
							in stationNames
						))
		rows = self.conn.execute(query) #pyright: ignore reportUnknownMemberType
		pids = [cast(int, row[st_procId]) for row in cast(Iterable[Row], rows)]
		for pid in pids:
			self.end_process(pid)
		self.unset_station_procs(pids)

	def _noop_startup(self, stationName: str) -> None:
		pid = self.get_pid()
		stmt = update(stations_tbl)\
				.values(procId = pid) \
				.where(func.lower(st_name) == func.lower(stationName))
		self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def _start_station_external_process(self, stationName: str) -> None:
		m = check_name_safety(stationName)
		if m:
			raise RuntimeError("Invalid station name was used")
		if platform.system() == "Darwin":
			return self._noop_startup(stationName)
		stationConf = f"{EnvManager.station_config_dir}/{stationName}.conf"
		subprocess.run(["mc-ices", "-c", f"'{stationConf}'", "-B"])

