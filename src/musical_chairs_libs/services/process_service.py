import os
import platform
import subprocess
import random
from typing import Optional, Iterable, cast, Union
from musical_chairs_libs.dtos_and_utilities import (
	check_name_safety,
	StationInfo
)
from sqlalchemy import (
	select,
	func,
	update
)
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_procId, st_ownerFk,
	users as users_tbl, u_username, u_pk
)
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

	def set_station_proc(self, stationId: int) -> None:
		pid = self.get_pid()
		stmt = update(stations_tbl)\
			.values(procId = pid) \
				.where(st_pk == stationId)
		self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def unset_station_procs(
		self,
		procIds: Optional[Iterable[int]]=None,
		stationIds: Union[int,Iterable[int], None]=None,
	) -> None:
		stmt = update(stations_tbl)\
			.values(procId = None)

		if isinstance(procIds, Iterable):
			stmt = stmt.where(st_procId.in_(procIds))
		elif type(stationIds) == int:
			stmt = stmt.where(st_pk == stationIds)
		elif isinstance(stationIds, Iterable):
			stmt = stmt.where(st_pk.in_(stationIds))
		else:
			raise ValueError("procIds, stationIds, or stationNames must be provided.")
		self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def enable_stations(self,
		stationKeys: Union[list[int],str],
		ownerKey: Union[int, str, None]
	) -> None:
		result: list[StationInfo] = []
		if type(stationKeys) == str and stationKeys == "*":
			result = list(self.station_service.get_stations(ownerKey=ownerKey))
		elif isinstance(stationKeys, list):
			result = list(self.station_service.get_stations(
				stationKeys=stationKeys
			))
		for station in result:
			self._start_station_external_process(station.name)

	def disable_stations(
		self,
		stationKeys: Union[list[int],str],
		ownerKey: Union[int, str, None]
	) -> None:
		query = select(st_procId).where(st_procId.is_not(None))
		if type(stationKeys) == str and stationKeys == "*":
			if type(ownerKey) == int:
				query = query.where(st_ownerFk == ownerKey)
			elif type(ownerKey) == str:
				query = query.join(users_tbl, u_pk == st_ownerFk)\
					.where(u_username == ownerKey)
		elif isinstance(stationKeys, list):
			query = query.where(st_pk.in_(stationKeys))

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
		stationConf = f"{EnvManager.station_config_dir}/ices.{stationName}.conf"
		if not os.path.isfile(stationConf):
			raise LookupError(f"Station not found at: {stationConf}")
		if platform.system() == "Darwin":
			return self._noop_startup(stationName)
		subprocess.run(["mc-ices", "-c", f"{stationConf}", "-B"])

