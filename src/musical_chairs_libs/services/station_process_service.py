from musical_chairs_libs.dtos_and_utilities import (
	StationInfo,
	get_datetime,
	AccountInfo,
	Lost
)
import musical_chairs_libs.dtos_and_utilities.logging as logging
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_procId,
	st_ownerFk, 
	users as user_tbl, u_username, u_pk, 
)
from sqlalchemy import (
	select,
	func,
	update,
)
from sqlalchemy.engine import Connection
from typing import (
	Iterator,
	Optional,
	cast,
	Iterable,
	Union,
	Collection,
	Sequence,
)
from .template_service import TemplateService
from .process_service import ProcessService
from .station_service import StationService
from .stations_albums_service import StationsAlbumsService

class StationProcessService:

	def __init__(
		self,
		conn: Optional[Connection]=None,
		templateService: Optional[TemplateService]=None,
		stationService: Optional[StationService]=None,
		stationsAlbumsService: Optional[StationsAlbumsService]=None
	):
		if not conn:
			raise RuntimeError("No connection provided")
		if not templateService:
			templateService = TemplateService()
		if not stationService:
			stationService = StationService(conn)
		if not stationsAlbumsService:
			stationsAlbumsService = StationsAlbumsService(conn)
		self.conn = conn
		self.template_service = templateService
		self.station_service = stationService
		self.stations_albums_service = stationsAlbumsService
		self.get_datetime = get_datetime


	def enable_stations(self,
		stations: Collection[StationInfo],
		owner: AccountInfo,
		includeAll: bool = False
	) -> Iterator[StationInfo]:
		stationsEnabled: Iterator[StationInfo] = iter([])
		if includeAll:
			canBeEnabled = {s[0] for s in  \
				self.station_service.get_station_song_counts(ownerId=owner.id) \
				if s[1] > 0
			}
			stationsEnabled = self.station_service.get_stations(
				stationKeys=canBeEnabled,
				ownerId=owner.id
			)
		else:
			canBeEnabled = {s[0] for s in  \
				self.station_service.get_station_song_counts(
					stationIds=(s.id for s in stations)
				) \
				if s[1] > 0
			}
			canBeEnabled |= {s[0] for s in  \
				self.stations_albums_service.get_station_song_counts(
					stationIds=(s.id for s in stations)
				) \
				if s[1] > 0
			}
			stationsEnabled = (s for s in stations if s.id in canBeEnabled)
			for station in stationsEnabled:
				if ProcessService.noop_mode():
					self.__noop_startup__(station.name)
					self.conn.commit()
				else:
					if not self.conn.engine.url.database:
						raise RuntimeError("db Name is missing")
					
					if not self.template_service.does_station_config_exist(
						station.name,
						owner.username
					):
						self.template_service.create_station_files(
							station.id,
							station.name,
							station.displayname,
							owner.username,
							station.bitratekps or 128
						)
					
					self.template_service.sync_station_password(
						station.name,
						owner.username
					)

					ProcessService.start_song_queue_process(
						self.conn.engine.url.database,
						station.name,
						owner.username
					)
				yield station

	def __noop_startup__(self, stationName: str) -> None:
		#for normal operations, this is handled in the ices process

		pid = ProcessService.get_pid()
		stmt = update(stations_tbl)\
				.values(procid = pid) \
				.where(func.lower(st_name) == func.lower(stationName))
		self.conn.execute(stmt)

	def unset_station_procs(
		self,
		procIds: Optional[Iterable[int]]=None,
		stationIds: Union[int,Sequence[int], None, Lost]=Lost(),
	) -> None:
		stmt = update(stations_tbl)\
			.values(procid = None)

		if isinstance(procIds, Iterable):
			stmt = stmt.where(st_procId.in_(procIds))
		elif type(stationIds) == int:
			stmt = stmt.where(st_pk == stationIds)
		elif isinstance(stationIds, Iterable):
			stmt = stmt.where(st_pk.in_(stationIds))
		elif stationIds is Lost():
			raise ValueError("procIds, stationIds, or stationNames must be provided.")
		self.conn.execute(stmt)

	def set_station_proc(self, stationId: int) -> None:
		pid = ProcessService.get_pid()
		stmt = update(stations_tbl)\
			.values(procid = pid) \
				.where(st_pk == stationId)
		self.conn.execute(stmt)
		self.conn.commit()


	def disable_stations(
		self,
		stationIds: Optional[Iterable[int]],
		ownerKey: Union[int, str, None]=None
	) -> None:
		#explicitly checking that stationIds is not null rather
		#simply if stationIds because we want want [] to trigger the all case
		stationIds = list(stationIds) if stationIds is not None else None
		logging.radioLogger.debug(
			f"disable {stationIds if stationIds is not None else 'All'}"
		)
		query = select(st_procId).where(st_procId.is_not(None))
		if ownerKey:
			if type(ownerKey) == int:
				query = query.where(st_ownerFk == ownerKey)
			elif type(ownerKey) == str:
				query = query.join(user_tbl, u_pk == st_ownerFk)\
					.where(u_username == ownerKey)
		else:
			if stationIds is not None:
				query = query.where(st_pk.in_(stationIds))
			

		rows = self.conn.execute(query)
		pids = [cast(int, row[0]) for row in rows]
		for pid in pids:
			logging.radioLogger.debug(f"send signal to {pid}")
			ProcessService.end_process(pid)
		self.unset_station_procs(stationIds=stationIds)
		self.conn.commit()