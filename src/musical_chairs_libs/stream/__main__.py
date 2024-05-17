import threading
import sys
import signal
import subprocess
from . import queue_song_source
from typing import Any
from musical_chairs_libs.services import (
	AlbumService,
	EnvManager,
	ArtistService,
	ProcessService,
	QueueService,
	StationService,
)
from threading import ExceptHookArgs, Thread
from setproctitle import setproctitle
import musical_chairs_libs.dtos_and_utilities.logging as logging
from musical_chairs_libs.services.fs import S3FileService



def handle_keyboard(sigNum: Any, frame: Any):
	logging.radioLogger.info("Received interupt")
	queue_song_source.stopSending = True
	queue_song_source.stopLoading = True

def handle_terminate_signal(sigNum: Any, frame: Any):
	logging.radioLogger.info("Received termination signal")
	queue_song_source.stopSending = True
	queue_song_source.stopLoading = True
	queue_song_source.clean_up_ices_process()

signal.signal(signal.SIGINT, handle_keyboard)
signal.signal(signal.SIGTERM, handle_terminate_signal)




def start_song_queue(dbName: str, stationName: str, ownerName: str):
	logging.radioLogger.info("Starting the queue process")
	logging.radioLogger.debug("Debug canary")

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
	
	conn = EnvManager.get_configured_radio_connection(dbName)


	stationService = StationService(conn)
	stationId = stationService.get_station_id(stationName, ownerName)
	if not stationId:
		raise RuntimeError(
			"station with owner"
			f" {ownerName} and name {stationName} not found"
		)
	
	artistService = ArtistService(conn)
	albumService = AlbumService(conn)
	fileService = S3FileService(artistService, albumService)
	queueService = QueueService(conn)
	stationService.set_station_proc(stationId)

	loadThread = Thread(
		target=queue_song_source.load_data,
		args=[stationId, queueService, fileService],
	)
	sendThread = Thread(
		target=queue_song_source.send_next,
		args=[start_ices]
	)

	def handle_loading_error(args: ExceptHookArgs):
		if args.thread == loadThread:
			conn.close()
		if args.thread == sendThread:
			queue_song_source.clean_up_ices_process()

	threading.excepthook = handle_loading_error

	try:
		loadThread.start()
		sendThread.start()

		while True:
			sendThread.join(30)
			if queue_song_source.stopLoading or queue_song_source.stopSending:
				break
		queue_song_source.stopLoading = True
		logging.radioLogger.debug("Escaped the loop")

		if not conn.closed:
			logging.radioLogger.info("Closing the connection")
			try:
				conn.close()
			except:
				logging.radioLogger.warn("Could not close the connection")
	finally:
		logging.radioLogger.info("Disabling the station")
		stationService.disable_stations([stationId])





if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]


	start_song_queue(dbName, stationName, ownerName)
	logging.radioLogger.info("Ending station queue process")
