import musical_chairs_libs.dtos_and_utilities.log_config as log_config
import socket
import subprocess
import time
from typing import (
	Any,
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
	StreamQueuedItem
)
from tempfile import NamedTemporaryFile
from threading import Condition, Lock
#seeing if I can get away with not using TracebackException with new
#log handlers
#from traceback import TracebackException


fileQueue = BlockingQueue[
	Tuple[Optional[BinaryIO], Optional[StreamQueuedItem]]
](size=3, retryInterval=30)
waiter = Condition()
stopRunning = False
icesProcess: Optional[subprocess.Popen[bytes]] = None
loaded = set[StreamQueuedItem]()
loadingLock = Lock()


def check_is_running(_: Any = None) -> bool:
	global stopRunning
	return not stopRunning


def stop():
	global stopRunning
	stopRunning = True


def get_song_info(
	stationId: int,
	songPopper: SongPopper
) -> Iterator[StreamQueuedItem]:
	global fileQueue
	while True:
		try:
			offset = fileQueue.qsize()
			log_config.queueLogger.debug(f"offset : {offset}")
			queueItem = songPopper.pop_next_queued(stationId, loaded)
			if not queueItem:
				log_config.radioLogger.info("Null queueItem - ending station")
				break
			with loadingLock:
				loaded.add(queueItem)
			yield queueItem
		except Exception as e:
			log_config.radioLogger.error("Error getting song info")
			log_config.radioLogger.error(e, exc_info=True)
			break
	stop()


def load_data(
		stationId: int,
		songPopper: SongPopper,
		fileService: FileService
	):
	log_config.radioLogger.info(f"Beginning data load")
	try:
		currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		for queueItem in get_song_info(
			stationId,
			songPopper
		):
			if not check_is_running():
				log_config.radioLogger.info(f"Stop running flag encountered")
				break
			log_config.queueLogger.info(f"queued: {queueItem.name}")
			attempts = 0
			while True:
				try:
					with fileService.open_song(queueItem.internalpath) as src:
						for chunk in src:
							currentFile.write(chunk)
					break
				except Exception as e:
					log_config.radioLogger.warning(e)
					attempts += 1
					if attempts > 3:
						log_config.radioLogger.error(
							f"Retried {attempts} times to download song"
						)
						raise
					currentFile.truncate(0)
					currentFile.seek(0)
					time.sleep(.25 * attempts)
			log_config.queueLogger.info(f"loaded: {queueItem.name}")
			fileQueue.put((currentFile, queueItem), check_is_running)
			currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
		fileQueue.put((None, None), check_is_running)
	
	except Exception as e:
		if isinstance(e, TimeoutError) and not check_is_running():
			log_config.radioLogger.debug("Queue has stopped waiting on put")
			return
		log_config.radioLogger.error("Error while trying to load data")
		log_config.radioLogger.error(e, exc_info=True)
	finally:
		stop()


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
			log_config.radioLogger.error("Socket timmed out")
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
		log_config.radioLogger.error(
			"Couldn't shut down socket. May already be closed"
		)


def clean_up_tmp_files():
	log_config.radioLogger.info("cleaning up tmp files")
	while fileQueue.qsize() > 0:
		unusedFile = fileQueue.get_unblocked()
		if unusedFile and unusedFile[0]:
			log_config.radioLogger.info(f"tmp file: {unusedFile[0].name}")
			unusedFile[0].close()


def clean_up_ices_process():
	global icesProcess
	if icesProcess:
		try:
			icesProcess.terminate()
			log_config.radioLogger.info("Process successfully terminated")
		except Exception as procError:
			log_config.radioLogger.error("Error terminating sub process")
			log_config.radioLogger.error(procError, exc_info=True)
	else:
		log_config.radioLogger.warning(
			"Can't clean up station process. It is null"
		)


def send_next(
		stationId: int,
		startSubProcess: Callable[[str], subprocess.Popen[bytes]],
		songPopper: SongPopper,
		timeout: int
	):
	global icesProcess
	currentFile = None
	queueItem = None
	skipped = False
	host = "127.0.0.1"
	portNumber = 0
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	log_config.radioLogger.info(f"Beginning data send")
	try:
		listener.bind((host, portNumber))
		listener.listen(1)
		icesProcess = startSubProcess(str(listener.getsockname()[1]))
		log_config.radioLogger.debug("Ices process started")
		conn = accept(listener, timeout)
		if not conn:
			log_config.radioLogger.error("No connection")
			return
		with conn:
			while True:
				returnCode = icesProcess.poll()
				if not returnCode is None:
					log_config.radioLogger.error("mc-ices errored out.")
					break
				if not check_is_running():
						log_config.radioLogger.warning("stopLoading is set")
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
					log_config.radioLogger.debug(f"closing {currentFile.name}")
					currentFile.close()
				with fileQueue.delayed_decrement_get(
					check_is_running
				) as (currentFile, queueItem):
					display = queueItem.display() if queueItem else "Missing Name"
					log_config.queueLogger.info(f"Playing: {display}")
					if queueItem:
						if not songPopper.move_from_queue_to_history(
							stationId,
							queueItem.id,
							queueItem.queuedtimestamp
						):
							log_config.radioLogger.info(
								f"Skipping {queueItem.name}"
							)
							skipped = True
							continue
						else:
							skipped = False
				if currentFile:
					log_config.queueLogger.info(f"Sending {currentFile.name} to ices.")
					conn.sendall(f"{currentFile.name}\n".encode())
					conn.sendall(f"{display}\n".encode())
				else:
					conn.sendall(b"\n\n")
					break
	except Exception as e:
		if isinstance(e, TimeoutError) and not check_is_running():
			log_config.radioLogger.debug("Queue has stopped waiting on get")
			return
		log_config.radioLogger.error(e, exc_info=True)
	finally:
		log_config.radioLogger.debug("send_next finally")
		stop()
		cleanup_socket(listener)
		clean_up_tmp_files()
		clean_up_ices_process()


