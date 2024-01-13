import sys
import signal
import subprocess
from . import queue_song_source
from typing import Any, Optional
from musical_chairs_libs.services import (
	ProcessService,
	EnvManager,
	StationService
)
from threading import Thread
import musical_chairs_libs.dtos_and_utilities.logging as logging

def handle_keyboard(sigNum: Any, frame: Any):
	print("Receive keyboard interupt")
	queue_song_source.stopSending = True
	queue_song_source.stopLoading = True

signal.signal(signal.SIGINT, handle_keyboard)


def get_station_id(
	stationName: str,
	ownerName: str,
	dbName: str
) -> Optional[int]:
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		stationId = StationService(conn).get_station_id(stationName, ownerName)
		return stationId
	except Exception as e:
		print(e)
	finally:
		conn.close()

def get_station_proc(
	dbName: str,
	stationId: int
):
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		StationService(conn).set_station_proc(stationId)
	except Exception as e:
		print(e)
	finally:
		conn.close()


def start_song_queue(dbName: str, stationName: str, ownerName: str):
	logging.logger.info("Starting the queue process")

	def start_ices(portNumber: str) -> subprocess.Popen[bytes]:
		return ProcessService.start_station_mc_ices(
			stationName,
			ownerName,
			portNumber
		)
	
	stationId = get_station_id(stationName, ownerName, dbName)
	if not stationId:
		raise RuntimeError(
			"station with owner"
			f" {ownerName} and name {stationName} not found"
		)
	get_station_proc(dbName, stationId)

	loadThread = Thread(
		target=queue_song_source.load_data,
		args=[dbName, stationId]
	)
	sendThread = Thread(
		target=queue_song_source.send_next,
		args=[start_ices]
	)

	loadThread.start()
	sendThread.start()

	while True:
		sendThread.join(30)
		if queue_song_source.stopLoading or queue_song_source.stopSending:
			break


	queue_song_source.stopLoading = True






if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]


	start_song_queue(dbName, stationName, ownerName)
