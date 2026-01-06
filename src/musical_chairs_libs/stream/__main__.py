import os
import threading
import sys
import signal
import subprocess
from . import queue_song_source
from typing import Any
from musical_chairs_libs.services import (
	ActionsHistoryManagementService,
	ActionsHistoryQueryService,
	AlbumQueueService,
	BasicUserProvider,
	CollectionQueueService,
	CurrentUserProvider,
	EmptyUserTrackingService,
	PathRuleService,
	PlaylistQueueService,
	ProcessService,
	QueueService,
	SongInfoService,
	StationService,
	StationProcessService,

)
from threading import ExceptHookArgs, Thread
from setproctitle import setproctitle
import musical_chairs_libs.dtos_and_utilities.logging as logging
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	StationTypes
)
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.services.fs import S3FileService
from sqlalchemy.engine import Connection

def __end_stream__():
	queue_song_source.stopRunning = True
	queue_song_source.clean_up_ices_process()

def handle_keyboard(sigNum: Any, frame: Any):
	logging.radioLogger.info("Received interupt")
	__end_stream__()

def handle_terminate_signal(sigNum: Any, frame: Any):
	logging.radioLogger.info("Received termination signal")
	__end_stream__()

signal.signal(signal.SIGINT, handle_keyboard)
signal.signal(signal.SIGTERM, handle_terminate_signal)

def close_db_connection(conn: Connection, connName: str):
	logging.radioLogger.info(f"Closing the {connName} connection")
	try:
		conn.close()
	except:
		logging.radioLogger.warning(f"Could not close the  {connName} connection")

def file_service() -> FileService:
	return S3FileService()

def path_rule_service(conn: Connection) -> PathRuleService:
	return PathRuleService(
		conn,
		file_service(),
		BasicUserProvider(None)
	)


def current_user_provider(conn: Connection) -> CurrentUserProvider:
	actionsHistoryQueryService = ActionsHistoryQueryService(conn)
	pathRuleService = path_rule_service(conn)

	currentUserProvider = CurrentUserProvider(
		BasicUserProvider(None),
		EmptyUserTrackingService(),
		actionsHistoryQueryService,
		pathRuleService
	)
	return currentUserProvider


def queue_service(conn: Connection) -> QueueService:
	currentUserProvider = current_user_provider(conn)
	actionsHistoryManagementService = ActionsHistoryManagementService(
		conn,
		EmptyUserTrackingService(),
		currentUserProvider
	)
	pathRuleService = path_rule_service(conn)
	songInfoService = SongInfoService(
		conn,
		currentUserProvider,
		pathRuleService
	)
	queueService = QueueService(
		conn,
		currentUserProvider,
		actionsHistoryManagementService,
		songInfoService,
		pathRuleService,
	)
	return queueService



def start_song_queue(dbName: str, stationName: str, ownerName: str):
	logging.radioLogger.info("Starting the queue process")
	logging.radioLogger.debug(f"Debug canary: {os.getcwd()}")

	def start_ices(portNumber: str) -> subprocess.Popen[bytes]:
		try:
			setproctitle(
				f"MC Radio - {ownerName}_{stationName} at {portNumber}"
			)
		except Exception as e:
			logging.radioLogger.info("Failed to rename process")
			logging.radioLogger.info(e)
		logging.radioLogger.info(f"Starting mc ices with {ownerName}_{stationName}")
		return ProcessService.start_station_mc_ices(
			stationName,
			ownerName,
			portNumber
		)

	readingConn = ConfigAcessors.get_configured_radio_connection(
		dbName,
		isolationLevel = "READ COMMITTED"
	)
	updatingConn = ConfigAcessors.get_configured_radio_connection(dbName)

	readingSongQueueService = queue_service(readingConn)
	updatingSongQueueService = queue_service(updatingConn)


	pathRuleService = path_rule_service(readingConn)
	stationService = StationService(
		readingConn,
		current_user_provider(readingConn),
		pathRuleService
	)
	stationId = stationService.get_station_id(stationName, ownerName)
	if not stationId:
		raise RuntimeError(
			"station with owner"
			f" {ownerName} and name {stationName} not found"
		)
	
	station = next(stationService.get_stations(stationId))

	queueServiceType = QueueService

	if station.typeid == StationTypes.ALBUMS_ONLY.value:
		queueServiceType = AlbumQueueService
	elif station.typeid == StationTypes.PLAYLISTS_ONLY.value:
		queueServiceType = PlaylistQueueService
	elif station.typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value:
		queueServiceType = CollectionQueueService

	fileService = file_service()
	
	readingQueueService = readingSongQueueService
	if queueServiceType != QueueService:
		readingQueueService = queueServiceType(  #pyright: ignore [reportCallIssue]
			readingConn,
			readingSongQueueService,
			current_user_provider(readingConn)
		)
	updatingQueueService = updatingSongQueueService
	if queueServiceType != QueueService:
		updatingQueueService = queueServiceType( #pyright: ignore [reportCallIssue]
			updatingConn,
			updatingQueueService,
			current_user_provider(readingConn)
		)
	stationProcessService = StationProcessService(
		updatingConn,
		current_user_provider(readingConn),
		stationService
	)
	stationProcessService.set_station_proc(stationId)

	loadThread = Thread(
		target=queue_song_source.load_data,
		args=[stationId, readingQueueService, fileService],
	)
	sendThread = Thread(
		target=queue_song_source.send_next,
		args=[
			stationId,
			start_ices,
			updatingQueueService,
			ProcessService.stream_timeout
		]
	)

	def handle_loading_error(args: ExceptHookArgs):
		if args.thread == loadThread:
			readingConn.close()
		if args.thread == sendThread:
			queue_song_source.clean_up_ices_process()

	threading.excepthook = handle_loading_error

	try:
		loadThread.start()
		sendThread.start()

		while queue_song_source.stopRunning:
			sendThread.join(30)
		sendThread.join() #wait for clean up to finish
		logging.radioLogger.debug("Escaped the loop")


	finally:
		logging.radioLogger.debug(
			f"Is loading thread alive? {loadThread.is_alive()}"
		)
		logging.radioLogger.debug(
			f"Is sending thread alive? {sendThread.is_alive()}"
		)
		logging.radioLogger.info("Disabling the station")
		stationProcessService.disable_stations(station)
		logging.radioLogger.debug("Station disabled")
		close_db_connection(readingConn, "reading")
		close_db_connection(updatingConn, "updating")





if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]

	try:
		start_song_queue(dbName, stationName, ownerName)
	except Exception as e:
		logging.radioLogger.error(e, exc_info=True)
	logging.radioLogger.info("End of station queue process")
