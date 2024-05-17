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
from musical_chairs_libs.protocols import (
	FileService,
	SongPopper
)
from musical_chairs_libs.dtos_and_utilities import BlockingQueue
from tempfile import NamedTemporaryFile
from threading import Condition
import musical_chairs_libs.dtos_and_utilities.logging as logging



fileQueue = BlockingQueue[Tuple[Optional[BinaryIO], Optional[str]]](3, 30)
waiter = Condition()
stopLoading = False
stopSending = False
icesProcess: Optional[subprocess.Popen[bytes]] = None



def get_song_info(
	stationId: int,
	songPopper: SongPopper,
) -> Iterator[
		Tuple[str, Union[str,None]]
	]:

	while True:
		try:
			(songPath, songName, album, artist) = \
				songPopper.pop_next_queued(stationId=stationId)
			if songName:
				display = f"{songName} - {album} - {artist}"
			else:
				display = os.path.splitext(os.path.split(songPath)[1])[0]
			display = display.replace("\n", "")
			yield songPath, display
		except Exception as e:
			logging.radioLogger.error("Error getting song info")
			logging.radioLogger.error(e)
			break


def load_data(
		stationId: int, 
		songPopper: SongPopper,
		fileService: FileService
	):
	global stopLoading
	global stopSending
	logging.radioLogger.info(f"Beginning data load")
	try:
		currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		for (filename, display) in get_song_info(stationId, songPopper):
			if stopLoading:
				logging.radioLogger.info(f"Stop loading flag encountered")
				break
			logging.radioLogger.info(f"file name: {filename}")
			with fileService.open_song(filename) as src:
				for chunk in src:
					currentFile.write(chunk)
			fileQueue.put((currentFile, display), lambda _: not stopLoading)
			currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		fileQueue.put((None, None), lambda _: not stopLoading)
	except Exception as e:
		logging.radioLogger.error("Error while trying to load data")
		logging.radioLogger.error(e)
		stopLoading = True
		stopSending = True

def accept(
	listener: socket.socket,
	timeout: int
) -> Optional[socket.socket]:
	global icesProcess
	listener.settimeout(timeout)
	while True:
		try:
			conn, _ = listener.accept()
			return conn
		except socket.timeout:
			logging.radioLogger.error("Socket timmed out")
			if icesProcess:
				returnCode = icesProcess.poll()
				if not returnCode is None:
					return None
			return None

def clean_up_tmp_files(listener: socket.socket):
	global stopLoading
	stopLoading = True
	try:
		listener.shutdown(socket.SHUT_RDWR)
		listener.close()
	except:
		logging.radioLogger.error(
			"Couldn't shut down socket. May already be closed"
		)
 
	logging.radioLogger.info("cleaning up unused")
	while True:
		unusedFile = fileQueue.unblocked_get()
		if unusedFile and unusedFile[0]:
			unusedFile[0].close()

def clean_up_ices_process():
	global icesProcess
	if icesProcess:
		try:
			icesProcess.terminate()
			logging.radioLogger.info("Process successfully terminated")
		except Exception as procError:
			logging.radioLogger.error("Error terminating sub process")
			logging.radioLogger.error(procError)
	else:
		logging.radioLogger.error(
			"Can't clean up station process. It is null"
		)


def send_next(
		startSubProcess: Callable[[str], subprocess.Popen[bytes]],
		timeout: int
	):
	global stopLoading
	global stopSending
	global icesProcess
	currentFile = None
	host = "127.0.0.1"
	portNumber = 0
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	logging.radioLogger.info(f"Beginning data send")
	try:
		listener.bind((host, portNumber))
		listener.listen(1)
		icesProcess = startSubProcess(str(listener.getsockname()[1]))
		logging.radioLogger.debug("Ices process started")
		conn = accept(listener, timeout)
		if not conn:
			logging.radioLogger.error("No connection")
			clean_up_tmp_files(listener)
			return
		with conn:
			while True:
				returnCode = icesProcess.poll()
				if not returnCode is None:
					logging.radioLogger.error("mc-ices errored out.")
					break
				if stopSending:
						logging.radioLogger.error("stopSending is set")
						break
				logging.radioLogger.debug("About receive signal byte")
				res = conn.recv(1)
				logging.radioLogger.debug(f"Received signal byte: {res}")
				if res == b"0":
					break
				if currentFile:
					currentFile.close()
				currentFile, display = fileQueue.get(lambda _: not stopSending)
				logging.radioLogger.info(f"From queue: {display}")
				if currentFile:
					conn.sendall(f"{currentFile.name}\n".encode())
					conn.sendall(f"{display}\n".encode())
				else:
					conn.sendall(b"\n\n")
					break
	except Exception as e:
		logging.radioLogger.error(e)
	finally:
		stopSending =  True
		clean_up_tmp_files(listener)
		clean_up_ices_process()


