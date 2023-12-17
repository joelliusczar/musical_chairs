import sys
import signal
import subprocess
from . import queue_song_source
from typing import Any
from musical_chairs_libs.services import (
	ProcessService
)
from threading import Thread


def handle_keyboard(sigNum: Any, frame: Any):
	print("Receive keyboard interupt")
	queue_song_source.stopSending = True
	queue_song_source.stopLoading = True

# signal.signal(signal.SIGINT, handle_keyboard)




def start_song_queue(dbName: str, stationName: str, ownerName: str):

	def start_ices(portNumber: str) -> subprocess.Popen[bytes]:
		return ProcessService.start_station_mc_ices(
			stationName,
			ownerName,
			portNumber
		)

	loadThread = Thread(
		target=queue_song_source.load_data,
		args=[dbName, stationName, ownerName]
	)
	sendThread = Thread(
		target=queue_song_source.send_next,
		args=[start_ices]
	)

	loadThread.start()
	sendThread.start()

	sendThread.join(600)

	queue_song_source.stopLoading = True






if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]


	start_song_queue(dbName, stationName, ownerName)
