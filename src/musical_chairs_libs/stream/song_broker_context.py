import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.protocols as mcp
import musical_chairs_libs.services as mcr
import musical_chairs_libs.services.fs as mcfs
import musical_chairs_libs.dtos_and_utilities.log_config as log_config
import typing


def file_service() -> mcp.FileService:
	return mcfs.FileServiceFactory.get_file_service()


class SongBrokerContext:

	def __init__(self, dbName: str, stationName: str, ownerName: str):
		self.db_name = dbName
		self.station_name = stationName
		self.owner_name = ownerName



	def close_db_connection(self):
		log_config.radioLogger.info("Closing the connection")
		try:
			self.conn.close()
		except:
			log_config.radioLogger.warning(f"Could not close the connection")

	def pick_song_popper(self) -> mcp.SongPopper:

		if self.station.typeid == dtos.StationTypes.SONGS_ONLY.value:
			return self.queueService
		else:
			return mcr.CollectionQueueService(
				self.conn,
				self.queueService,
				self.currentUserProvider
			)

	def __enter__(
		self,
	) -> "SongBrokerContext":
		self.conn = dtos.DbConnectionProvider.get_configured_radio_connection(
			self.db_name,
			isolationLevel = "READ COMMITTED"
		)
		try:
			self.pathRuleService = mcr.PathRuleService(
				self.conn,
				file_service(),
				mcr.BasicUserProvider(None)
			)
			self.currentUserProvider = mcr.CurrentUserProvider(
				mcr.BasicUserProvider(None),
				mcr.EmptyUserTrackingService(),
				self.pathRuleService
			)
			songInfoService = mcr.SongInfoService(
				self.conn,
				self.currentUserProvider,
				self.pathRuleService
			)
			self.queueService = mcr.QueueService(
				self.conn,
				self.currentUserProvider,
				songInfoService,
				self.pathRuleService,
			)
			stationService = mcr.StationService(
				self.conn,
				self.currentUserProvider,
				self.pathRuleService
			)
			self.station = next(iter(stationService.get_stations(
				self.station_name,
				self.owner_name,
				exactStrMatch=True)))
			self.stationProcessService = mcr.StationProcessService(
				self.conn,
				self.currentUserProvider,
				stationService
			)
			return self
		except:
			self.close_db_connection()
			raise
		

	def __exit__(self, 
		exc_type: typing.Any,
		exc_value: typing.Any,
		traceback: typing.Any
	):
			self.close_db_connection()
		