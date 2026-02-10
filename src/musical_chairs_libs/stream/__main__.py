import os
import sys
import signal
import subprocess
from . import queue_song_source
from typing import Any
from musical_chairs_libs.services import (
	BasicUserProvider,
	CollectionQueueService,
	CurrentUserProvider,
	EmptyUserTrackingService,
	PathRuleService,
	ProcessService,
	QueueService,
	SongInfoService,
	StationService,
	StationProcessService,
)
from threading import Thread
from setproctitle import setproctitle
import musical_chairs_libs.dtos_and_utilities.log_config as log_config
from musical_chairs_libs.dtos_and_utilities import (
	DbConnectionProvider,
	StationTypes
)
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.services.fs import S3FileService
from sqlalchemy.engine import Connection

def __end_stream__():
	queue_song_source.stopRunning = True
	queue_song_source.clean_up_ices_process()


def handle_keyboard(sigNum: Any, frame: Any):
	log_config.radioLogger.info("Received interupt")
	__end_stream__()


def handle_terminate_signal(sigNum: Any, frame: Any):
	log_config.radioLogger.info("Received termination signal")
	__end_stream__()


signal.signal(signal.SIGINT, handle_keyboard)
signal.signal(signal.SIGTERM, handle_terminate_signal)


def close_db_connection(conn: Connection, connName: str):
	log_config.radioLogger.info(f"Closing the {connName} connection")
	try:
		conn.close()
	except:
		log_config.radioLogger.warning(f"Could not close the  {connName} connection")


def file_service() -> FileService:
	return S3FileService()


def path_rule_service(conn: Connection) -> PathRuleService:
	return PathRuleService(
		conn,
		file_service(),
		BasicUserProvider(None)
	)


def current_user_provider(conn: Connection) -> CurrentUserProvider:
	pathRuleService = path_rule_service(conn)

	currentUserProvider = CurrentUserProvider(
		BasicUserProvider(None),
		EmptyUserTrackingService(),
		pathRuleService
	)
	return currentUserProvider


def queue_service(conn: Connection) -> QueueService:
	currentUserProvider = current_user_provider(conn)
	pathRuleService = path_rule_service(conn)
	songInfoService = SongInfoService(
		conn,
		currentUserProvider,
		pathRuleService
	)
	queueService = QueueService(
		conn,
		currentUserProvider,
		songInfoService,
		pathRuleService,
	)
	return queueService


def start_ices(portNumber: str) -> subprocess.Popen[bytes]:
		try:
			setproctitle(
				f"MC Radio - {ownerName}_{stationName} at {portNumber}"
			)
		except Exception as e:
			log_config.radioLogger.info("Failed to rename process")
			log_config.radioLogger.info(e)
		log_config.radioLogger.info(
			f"Starting mc ices with {ownerName}_{stationName}"
		)
		return ProcessService.start_station_mc_ices(
			stationName,
			ownerName,
			portNumber
		)


def launch_loading(stationName: str, ownerName: str):
	conn = DbConnectionProvider.get_configured_radio_connection(
		dbName,
		isolationLevel = "READ COMMITTED"
	)
	pathRuleService = path_rule_service(conn)
	currentUserProvider = current_user_provider(conn)
	stationService = StationService(
		conn,
		currentUserProvider,
		pathRuleService
	)
	station = next(iter(stationService.get_stations(stationName, ownerName)))
	stationProcessService = StationProcessService(
		conn,
		currentUserProvider,
		stationService
	)
	stationProcessService.set_station_proc(station.id)
	queueService = queue_service(conn)
	fileService = file_service()
	try:
		if station.typeid == StationTypes.SONGS_ONLY.value:
			queue_song_source.load_data(station.id, queueService, fileService)
		else:
			collectionQueueService = CollectionQueueService(
				conn,
				queueService,
				currentUserProvider
			)
			queue_song_source.load_data(
				station.id,
				collectionQueueService,
				fileService
			)
	except:
		stationProcessService.unset_station_procs(stationIds=station.id)
		raise
	finally:
		close_db_connection(conn, "loading")


def launch_sending(stationName: str, ownerName: str):
	
	conn = DbConnectionProvider.get_configured_radio_connection(
		dbName,
		isolationLevel = "READ COMMITTED"
	)
	queueService = queue_service(conn)
	pathRuleService = path_rule_service(conn)
	currentUserProvider = current_user_provider(conn)
	stationService = StationService(
		conn,
		currentUserProvider,
		pathRuleService
	)
	station = next(iter(stationService.get_stations(stationName, ownerName)))
	try:

		if station.typeid == StationTypes.SONGS_ONLY.value:
			queue_song_source.send_next(
				station.id,
				start_ices,
				queueService,
				ProcessService.stream_timeout
			)
		else:
			collectionQueueService = CollectionQueueService(
				conn,
				queueService,
				currentUserProvider
			)
			queue_song_source.send_next(
				station.id,
				start_ices,
				collectionQueueService,
				ProcessService.stream_timeout
			)
	finally:
		close_db_connection(conn, "sending")
		queue_song_source.clean_up_ices_process()




def start_song_queue(dbName: str, stationName: str, ownerName: str):
	log_config.radioLogger.info("Starting the queue process")
	log_config.radioLogger.debug(f"Debug canary: {os.getcwd()}")

	loadThread = Thread(
		target=launch_loading,
		args=[stationName, ownerName],
	)
	sendThread = Thread(
		target=launch_sending,
		args=[stationName, ownerName]
	)


	try:
		loadThread.start()
		sendThread.start()

		while queue_song_source.stopRunning:
			sendThread.join(30)
		sendThread.join() #wait for clean up to finish
		log_config.radioLogger.debug("Escaped the loop")


	finally:
		log_config.radioLogger.debug(
			f"Is loading thread alive? {loadThread.is_alive()}"
		)
		log_config.radioLogger.debug(
			f"Is sending thread alive? {sendThread.is_alive()}"
		)
		log_config.radioLogger.info("Disabling the station")
		log_config.radioLogger.debug("Station disabled")





if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]

	try:
		start_song_queue(dbName, stationName, ownerName)
	except Exception as e:
		log_config.radioLogger.error(e, exc_info=True)
	log_config.radioLogger.info("End of station queue process")