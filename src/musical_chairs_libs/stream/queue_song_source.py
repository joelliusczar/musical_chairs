import sys
import os
import socket
from typing import (
	Tuple,
	Union,
	Iterator,
	BinaryIO,
	Optional,
	cast,
	Callable
)
from musical_chairs_libs.services.fs import S3FileService
from musical_chairs_libs.services import (
	EnvManager,
	QueueService,
	StationService
)
from tempfile import NamedTemporaryFile
from queue import SimpleQueue
from threading import Condition

fileQueue = SimpleQueue[Tuple[Optional[BinaryIO], Optional[str]]]()
waiter = Condition()
stopLoading = False
stopSending = False
maxSize = 5

def wait_for_queue():
	global stopLoading
	global stopSending
	try:
		waiter.acquire()
		waiter.wait(30)
		waiter.release()
	except Exception as e:
		print(e)
		stopSending = True
		stopLoading = True


def queue_ready():
	waiter.acquire()
	waiter.notify()
	waiter.release()


def get_song_info(
	stationId: int,
	dbName: str
) -> Iterator[
		Tuple[str, Union[str,None]]
	]:

	while True:
		conn = EnvManager.get_configured_radio_connection(dbName)
		try:
			queueService = QueueService(conn)
			(songPath, songName, album, artist) = \
				queueService.pop_next_queued(stationId=stationId)
			if songName:
				display = f"{songName} - {album} - {artist}"
			else:
				display = os.path.splitext(os.path.split(songPath)[1])[0]
			yield songPath, display
		except:
			break
		finally:
			conn.close()

def get_station_id(
	stationName: str,
	ownerName: str,
	dbName: str
) -> Optional[int]:
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		stationId = StationService(conn).get_station_id(stationName, ownerName)
		return stationId
	finally:
		conn.close()


def load_data(dbName: str, stationName: str, ownerName: str):
	global stopLoading
	global stopSending
	try:
		stationId = get_station_id(stationName, ownerName, dbName)
		if not stationId:
			raise RuntimeError(
				"station with owner"
				f" {ownerName} and name {stationName} not found"
			)
		currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		for (filename, display) in get_song_info(stationId, dbName):
			notified = False
			if stopLoading:
				break
			while fileQueue.qsize() > maxSize:
				wait_for_queue()
				if stopLoading:
					break
			fileQueue.put((currentFile, display))
			fileService = S3FileService()
			with fileService.open_song(filename) as src:
				for chunk in src:
					currentFile.write(chunk)
					if not notified:
						queue_ready()
			currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		while fileQueue.qsize() > maxSize:
			wait_for_queue()
			if stopLoading:
				return
		fileQueue.put((None, None))
		queue_ready()
	except Exception as e:
		print(e)
		stopLoading = True
		stopSending = True


def send_next(onAddressBind: Callable[[str], None]):
	global stopLoading
	global stopSending
	currentFile = None
	host = "127.0.0.1"
	portNumber = 50009
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		# listener.settimeout(5)
		listener.bind((host, portNumber))
		listener.listen(1)
		onAddressBind(str(listener.getsockname()[1]))
		conn, _ = listener.accept()
		with conn:
			while True:
				if stopSending:
						break
				res = conn.recv(1)
				if res == b"0":
					break
				if currentFile:
					currentFile.close()
				while fileQueue.qsize() < 1:
					wait_for_queue()
					if stopSending:
						break
				currentFile, display = fileQueue.get()
				queue_ready()
				if currentFile:
					conn.sendall(f"{currentFile.name}\n".encode())
					conn.sendall(f"{display}\n".encode())
				else:
					conn.sendall(b"")
					break
	except BrokenPipeError:
		devnull = os.open(os.devnull, os.O_WRONLY)
		os.dup2(devnull, sys.stdout.fileno())
	finally:
		stopLoading = True
		queue_ready()
		try:
			listener.shutdown(socket.SHUT_RDWR)
			listener.close()
		except:
			print("Couldn't shut down socket. May already be closed")


