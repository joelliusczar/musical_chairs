import os
import socket
import subprocess
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
	QueueService
)
from musical_chairs_libs.dtos_and_utilities import BlockingQueue
from tempfile import NamedTemporaryFile
from threading import Condition

fileQueue = BlockingQueue[Tuple[Optional[BinaryIO], Optional[str]]](3, 30)
waiter = Condition()
stopLoading = False
stopSending = False



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
			display = display.replace("\n", "")
			yield songPath, display
		except Exception as e:
			print("Error getting song info")
			print(e)
			break
		finally:
			conn.close()


def load_data(dbName: str, stationId: int):
	global stopLoading
	global stopSending
	try:
		currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		for (filename, display) in get_song_info(stationId, dbName):
			if stopLoading:
				break
			fileService = S3FileService()
			with fileService.open_song(filename) as src:
				for chunk in src:
					currentFile.write(chunk)
			fileQueue.put((currentFile, display), lambda _: not stopLoading)
			currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		fileQueue.put((None, None), lambda _: not stopLoading)
	except Exception as e:
		print(e)
		stopLoading = True
		stopSending = True

def accept(
	listener: socket.socket,
	proc: subprocess.Popen[bytes]
) -> Optional[socket.socket]:
	listener.settimeout(5)
	while True:
		try:
			conn, _ = listener.accept()
			return conn
		except socket.timeout:
			print("Socket timmed out")
			returnCode = proc.poll()
			if not returnCode is None:
				return None

def clean_up(listener: socket.socket):
	global stopLoading
	stopLoading = True
	try:
		listener.shutdown(socket.SHUT_RDWR)
		listener.close()
	except:
		print("Couldn't shut down socket. May already be closed")
 
	print("cleaning up unused")
	while True:
		unusedFile = fileQueue.unblocked_get()
		if unusedFile and unusedFile[0]:
			unusedFile[0].close()


def send_next(startSubProcess: Callable[[str], subprocess.Popen[bytes]]):
	global stopLoading
	global stopSending
	currentFile = None
	host = "127.0.0.1"
	portNumber = 50009
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proc: Optional[subprocess.Popen[bytes]] = None
	try:
		listener.bind((host, portNumber))
		listener.listen(1)
		proc = startSubProcess(str(listener.getsockname()[1]))
		conn = accept(listener, proc)
		if not conn:
			clean_up(listener)
			return
		with conn:
			while True:
				returnCode = proc.poll()
				if not returnCode is None:
					break
				if stopSending:
						break
				res = conn.recv(1)
				if res == b"0":
					break
				if currentFile:
					currentFile.close()
				currentFile, display = fileQueue.get(lambda _: not stopSending)
				if currentFile:
					conn.sendall(f"{currentFile.name}\n".encode())
					conn.sendall(f"{display}\n".encode())
				else:
					conn.sendall(b"\n\n")
					break
	except Exception as e:
		print(e)
	finally:
		clean_up(listener)
		if proc:
			try:
				proc.terminate()
			except Exception as procError:
				print("Error terminating sub process")
				print(procError)


