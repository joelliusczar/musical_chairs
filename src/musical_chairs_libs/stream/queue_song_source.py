import musical_chairs_libs.dtos_and_utilities.logging as logging
import socket
import subprocess
from typing import (
	BinaryIO,
	Callable,
	cast,
	Iterator,
	Optional,
	Tuple,
)
from musical_chairs_libs.protocols import (
	FileService,
	SongPopper
)
from musical_chairs_libs.dtos_and_utilities import (
	BlockingQueue,
	SongListDisplayItem
)
from tempfile import NamedTemporaryFile
from threading import Condition, Lock
from traceback import TracebackException


fileQueue = BlockingQueue[
	Tuple[Optional[BinaryIO], Optional[SongListDisplayItem]]
](3, 30)
waiter = Condition()
stopRunning = False
icesProcess: Optional[subprocess.Popen[bytes]] = None
loaded = set[SongListDisplayItem]()
loadingLock = Lock()



def get_song_info(
	stationId: int,
	songPopper: SongPopper
) -> Iterator[SongListDisplayItem]:
	global fileQueue
	while True:
		try:
			offset = fileQueue.qsize()
			logging.queueLogger.debug(f"offset : {offset}")
			queueItem = songPopper.pop_next_queued(stationId, loaded)
			with loadingLock:
				loaded.add(queueItem)
			yield queueItem
		except Exception as e:
			logging.radioLogger.error("Error getting song info")
			logging.radioLogger.error(e)
			break


def load_data(
		stationId: int,
		songPopper: SongPopper,
		fileService: FileService
	):
	global stopRunning
	logging.radioLogger.info(f"Beginning data load")
	try:
		currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		for queueItem in get_song_info(
			stationId,
			songPopper
		):
			if stopRunning:
				logging.radioLogger.info(f"Stop running flag encountered")
				break
			logging.queueLogger.info(f"queued: {queueItem.name}")
			with fileService.open_song(queueItem.internalpath) as src:
				for chunk in src:
					currentFile.write(chunk)
			fileQueue.put((currentFile, queueItem), lambda _: not stopRunning)
			currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		fileQueue.put((None, None), lambda _: not stopRunning)
	except Exception as e:
		logging.radioLogger.error("Error while trying to load data")
		logging.radioLogger.error(
			"".join(TracebackException.from_exception(e).format())
		)
	finally:
		stopRunning = True

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

def cleanup_socket(listener: socket.socket):
	try:
		listener.shutdown(socket.SHUT_RDWR)
		listener.close()
	except:
		logging.radioLogger.error(
			"Couldn't shut down socket. May already be closed"
		)

def clean_up_tmp_files():
	logging.radioLogger.info("cleaning up tmp files")
	while fileQueue.qsize() > 0:
		unusedFile = fileQueue.get_unblocked()
		if unusedFile and unusedFile[0]:
			logging.radioLogger.info(f"tmp file: {unusedFile[0].name}")
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
		stationId: int,
		startSubProcess: Callable[[str], subprocess.Popen[bytes]],
		songPopper: SongPopper,
		timeout: int
	):
	global stopRunning
	global icesProcess
	currentFile = None
	queueItem = None
	skipped = False
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
			return
		with conn:
			while True:
				returnCode = icesProcess.poll()
				if not returnCode is None:
					logging.radioLogger.error("mc-ices errored out.")
					break
				if stopRunning:
						logging.radioLogger.warning("stopLoading is set")
						break
				#don't want to wait for 'next' signal from ices when it doesn't
				#hasn't had anything to process
				if not skipped:
					res = conn.recv(1)
					if res == b"0":
						break
				if queueItem:
					with loadingLock:
						loaded.remove(queueItem)
				if currentFile:
					logging.radioLogger.debug(f"closing {currentFile.name}")
					currentFile.close()
				with fileQueue.delayed_decrement_get(
					lambda _: not stopRunning
				) as (currentFile, queueItem):
					display = queueItem.display() if queueItem else "Missing Name"
					logging.queueLogger.info(f"Playing: {display}")
					if queueItem:
						if not songPopper.move_from_queue_to_history(
							stationId,
							queueItem.id,
							queueItem.queuedtimestamp
						):
							logging.radioLogger.info(
								f"Skipping {queueItem.name}"
							)
							skipped = True
							continue
						else:
							skipped = False
				if currentFile:
					logging.queueLogger.info(f"Sending {currentFile.name} to ices.")
					conn.sendall(f"{currentFile.name}\n".encode())
					conn.sendall(f"{display}\n".encode())
				else:
					conn.sendall(b"\n\n")
					break
	except Exception as e:
		logging.radioLogger.error(
			"".join(TracebackException.from_exception(e).format())
		)
	finally:
		logging.radioLogger.debug("send_next finally")
		stopRunning = True
		cleanup_socket(listener)
		clean_up_tmp_files()
		clean_up_ices_process()


