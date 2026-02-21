import musical_chairs_libs.dtos_and_utilities as dtos
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	StationInfo,
	get_datetime,
	Lost,
)
import musical_chairs_libs.dtos_and_utilities.log_config as log_config
from musical_chairs_libs.tables import (
	stations as stations_tbl, st_pk, st_name, st_procId,
	st_ownerFk,
)
from pathlib import Path
from sqlalchemy import (
	select,
	func,
	update,
)
from sqlalchemy.engine import Connection
from typing import (
	Optional,
	cast,
	Iterable,
	Sequence,
)
from .current_user_provider import CurrentUserProvider
from .template_service import TemplateService
from .process_service import ProcessService
from .station_service import StationService
from .stations_albums_service import StationsAlbumsService

class StationProcessService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
		stationService: StationService,
		templateService: Optional[TemplateService]=None,
		stationsAlbumsService: Optional[StationsAlbumsService]=None
	):
		if not conn:
			raise RuntimeError("No connection provided")
		if not templateService:
			templateService = TemplateService()
		if not stationsAlbumsService:
			stationsAlbumsService = StationsAlbumsService(
				conn,
				stationService,
				currentUserProvider,
			)
		self.conn = conn
		self.template_service = templateService
		self.station_service = stationService
		self.stations_albums_service = stationsAlbumsService
		self.get_datetime = get_datetime
		self.current_user_provider = currentUserProvider


	def ensure_active_station_files(self, station: StationInfo):
		if not station.owner:
			raise RuntimeError("Station owner is not loaded")
		filePath = f"{ConfigAcessors.station_queue_files_dir()}"\
			f"/{station.owner.username}/{station.name}.jsonl"
		path = Path(filePath)
		path.parent.mkdir(parents=True, exist_ok=True)

		path.touch()


	def enable_stations(
		self,
		station:StationInfo | None
	) -> list[StationInfo]:
		with self.conn.begin() as transaction:
			if not station:
				user = self.current_user_provider.current_user()
				canBeEnabled = {s[0] for s in  \
					self.station_service.get_station_song_counts(ownerId=user.id) \
					if s[1] > 0
				}
				stationsEnabled = self.station_service.get_stations(
					stationKeys=canBeEnabled,
					ownerKey=user.id
				)
				return stationsEnabled
			else:
				canBeEnabled = {s[0] for s in  \
					self.station_service.get_station_song_counts(
						stationIds=[station.decoded_id()]
					) \
					if s[1] > 0
				}
				canBeEnabled |= {s[0] for s in  \
					self.stations_albums_service.get_station_song_counts(
						stationIds=[station.decoded_id()]
					) \
					if s[1] > 0
				}
				stationsEnabled = [
					s for s in [station] if s.decoded_id() in canBeEnabled
				]
				for station in stationsEnabled:
					if ProcessService.noop_mode():
						self.__noop_startup__(station.name)
						transaction.commit()
					else:
						if not self.conn.engine.url.database:
							raise RuntimeError("db Name is missing")
						if not station.owner or not station.owner.username:
							raise RuntimeError(f"{station.name} is missing owner")
						
						if not self.template_service.does_station_config_exist(
							station.name,
							station.owner.username
						):
							self.template_service.create_station_files(
								station.decoded_id(),
								station.name,
								station.displayname,
								station.owner.username,
								station.bitratekps or 128
							)
						
						self.template_service.sync_station_password(
							station.name,
							station.owner.username
						)
						self.ensure_active_station_files(station)

						ProcessService.start_song_queue_process(
							self.conn.engine.url.database,
							station.name,
							station.owner.username
						)
				return stationsEnabled


	def __noop_startup__(self, stationName: str) -> None:
		#for normal operations, this is handled in the ices process

		pid = ProcessService.get_pid()
		stmt = update(stations_tbl)\
				.values(procid = pid) \
				.where(func.lower(st_name) == func.lower(stationName))
		self.conn.execute(stmt)


	def unset_station_procs(
		self,
		procIds: Iterable[int] | None=None,
		stationIds: int |Sequence[int] | None | Lost=Lost()
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
		with self.conn.begin() as transaction:
			self.conn.execute(stmt)
			transaction.commit()


	def set_station_proc(self, stationId: int) -> None:
		pid = ProcessService.get_pid()
		stmt = update(stations_tbl)\
			.values(procid = pid) \
				.where(st_pk == stationId)
		with self.conn.begin() as transaction:
			self.conn.execute(stmt)
			transaction.commit()


	def disable_stations(
		self,
		station: StationInfo | None
	) -> None:

		log_config.radioLogger.debug(
			f"disable {station.id if station is not None else 'All'}"
		)
		query = select(st_procId).where(st_procId.is_not(None))
		if station is None:
			ownerKey = self.current_user_provider.current_user().id
			query = query.where(st_ownerFk == ownerKey)
		else:
			query = query.where(st_pk == station.decoded_id())
			
		with dtos.open_transaction(self.conn):
			rows = self.conn.execute(query).fetchall()
			pids = [cast(int, row[0]) for row in rows]
			for pid in pids:
				log_config.radioLogger.debug(f"send signal to {pid}")
				ProcessService.end_process(pid)
		