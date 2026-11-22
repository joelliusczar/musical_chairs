import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.dtos_and_utilities.log_config as log_config
import musical_chairs_libs.protocols as mcp
import socket
import subprocess
import threading
import time
import typing
from sqlalchemy.exc import OperationalError
from tempfile import NamedTemporaryFile
#seeing if I can get away with not using TracebackException with new
#log handlers
#from traceback import TracebackException

class SongBroker:

	def __init__(
		self,
		loadingPopper: mcp.SongPopper,
		sendingPopper: mcp.SongPopper,
		station: dtos.StationInfo,
		fileService: mcp.FileService,
		startSubProcess: typing.Callable[[str], subprocess.Popen[bytes]]
	) -> None:
		self.fileQueue = dtos.BlockingQueue[
			typing.Tuple[typing.BinaryIO | None, dtos.StreamQueuedItem | None]
		](size=3, retryInterval=30)
		self.stopRunning = False
		self.icesProcess: subprocess.Popen[bytes] | None = None
		self.loaded = set[dtos.StreamQueuedItem]()
		self.loadingLock = threading.Lock()
		self.loading_popper = loadingPopper
		self.sending_popper = sendingPopper
		self.station = station
		self.fileService = fileService
		self.startSubProcess = startSubProcess
		self.currentFile: typing.BinaryIO | None = None
		self.queueItem: dtos.StreamQueuedItem | None = None


	def check_is_running(self) -> bool:
		return not self.stopRunning


	def stop(self):
		self.stopRunning = True


	def pop_next_with_retry(
		self
	) -> dtos.StreamQueuedItem | None:
		attempts = 0
		while True:
			try:
				return self.loading_popper.pop_next_queued(
					self.station.decoded_id(), 
					self.loaded)
			except OperationalError:
				attempts += 1
				log_config.radioLogger.warning(f"Database error. Attempt: {attempts}")
				if attempts > 3:
					log_config.radioLogger.error(
						f"Retried {attempts} times to avoid database issue"
					)
					raise



	def get_song_info(self) -> typing.Iterator[dtos.StreamQueuedItem]:
		while True:
			try:
				offset = self.fileQueue.qsize()
				log_config.queueLogger.debug(f"offset : {offset}")
				queueItem = self.pop_next_with_retry()
				if not queueItem:
					log_config.radioLogger.info("Null queueItem - ending station")
					break
				with self.loadingLock:
					self.loaded.add(queueItem)
				yield queueItem
			except Exception as e:
				log_config.radioLogger.error("Error getting song info")
				log_config.radioLogger.error(e, exc_info=True)
				break
		self.stop()


	def load_loop(self):
		log_config.radioLogger.info(f"Beginning data load")

		try:
			currentFile = typing.cast(typing.BinaryIO, NamedTemporaryFile(mode="wb"))
			for queueItem in self.get_song_info():
				if not self.check_is_running():
					log_config.radioLogger.info(f"Stop running flag encountered")
					break
				log_config.queueLogger.info(f"queued: {queueItem.name}")
				attempts = 0
				while True:
					try:
						with self.fileService.open_song(queueItem.internalpath) as src:
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
				self.fileQueue.put(
					(currentFile, queueItem), 
					lambda _: self.check_is_running()
				)
				currentFile = typing.cast(
					typing.BinaryIO, 
					NamedTemporaryFile(mode="wb")
				)
			self.fileQueue.put(
				(None, None),
				lambda _: self.check_is_running()
			)
		
		except Exception as e:
			if isinstance(e, TimeoutError) and not self.check_is_running():
				log_config.radioLogger.debug("Queue has stopped waiting on put")
				log_config.radioLogger.warning(e, exc_info=True)
				return
			log_config.radioLogger.error("Error while trying to load data")
			log_config.radioLogger.error(e, exc_info=True)
		finally:
			log_config.radioLogger.debug("load_data finally")
			self.stop()


	def accept(
		self,
		listener: socket.socket,
		timeout: int
	) -> socket.socket | None:
		listener.settimeout(timeout)
		while True:
			try:
				conn, _ = listener.accept()
				return conn
			except socket.timeout:
				log_config.radioLogger.error("Socket timed out")
				if self.icesProcess:
					returnCode = self.icesProcess.poll()
					if not returnCode is None:
						return None
				return None


	def cleanup_socket(self, listener: socket.socket):
		try:
			listener.shutdown(socket.SHUT_RDWR)
			listener.close()
		except:
			log_config.radioLogger.error(
				"Couldn't shut down socket. May already be closed"
			)


	def clean_up_tmp_files(self):
		log_config.radioLogger.info("cleaning up tmp files")
		disposara = self.fileQueue.drain()
		for unusedFile in disposara:
			if unusedFile and unusedFile[0]:
				log_config.radioLogger.info(f"tmp file: {unusedFile[0].name}")
				unusedFile[0].close()


	def clean_up_ices_process(self):
		if self.icesProcess:
			try:
				self.icesProcess.terminate()
				log_config.radioLogger.info("Process successfully terminated")
			except Exception as procError:
				log_config.radioLogger.error("Error terminating sub process")
				log_config.radioLogger.error(procError, exc_info=True)
		else:
			log_config.radioLogger.warning(
				"Can't clean up station process. It is null"
			)

	def move_to_history_with_retry(
		self,
		queueItem: dtos.StreamQueuedItem
	) -> bool:
		attempts = 0
		while True:
			try:
				return self.sending_popper.move_from_queue_to_history(
					self.station.decoded_id(),
					queueItem.id,
					queueItem.queuedtimestamp
				)
			except OperationalError:
				attempts += 1
				log_config.radioLogger.warning(f"Database error. Attempt: {attempts}")
				if attempts > 3:
					log_config.radioLogger.error(
						f"Retried {attempts} times to avoid database issue"
					)
					raise

	def close_current_file(self):
		if self.queueItem:
			with self.loadingLock:
				self.loaded.discard(self.queueItem)
			self.queueItem = None
		if self.currentFile:
			log_config.radioLogger.debug(f"closing {self.currentFile.name}")
			self.currentFile.close()
			self.currentFile = None


	def set_current_song(self, 
		currentFile: typing.BinaryIO | None,
		queueItem: dtos.StreamQueuedItem | None
		) -> bool:
		self.currentFile = currentFile
		self.queueItem = queueItem
		if self.queueItem:
			if not self.move_to_history_with_retry(self.queueItem):
				log_config.radioLogger.info(
					f"Skipping {self.queueItem.name}"
				)
				return False
		return True

	def send_next(self, socketConn: socket.socket) -> bool:
		if self.currentFile:
			log_config.queueLogger.info(
				f"Sending {self.currentFile.name} to ices."
			)
			socketConn.sendall(f"{self.currentFile.name}\n".encode())
			display = self.queueItem.display() \
				if self.queueItem else "Missing Name"
			socketConn.sendall(f"{display}\n".encode())
			return True
		else:
			log_config.radioLogger.debug(
				f"{self.queueItem.id if self.queueItem else "No Queue Item"}"
			)
			socketConn.sendall(b"\n\n")
			return False


	def check_subprocess(self) -> bool:
		if self.icesProcess:
			returnCode = self.icesProcess.poll()
			if not returnCode is None:
				log_config.radioLogger.error("mc-ices errored out.")
				return False
			if not self.check_is_running():
				log_config.radioLogger.warning("stopLoading is set")
				return False
			return True
		return False

	def send_loop(
			self,
			timeout: int
		) -> bool:
		skipped = False
		listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		log_config.radioLogger.info(f"Beginning data send")
		try:
			listener.bind(("127.0.0.1", 0))
			listener.listen(1)
			self.icesProcess = self.startSubProcess(str(listener.getsockname()[1]))
			log_config.radioLogger.debug("Ices process started")
			socketConn = self.accept(listener, timeout)
			if not socketConn:
				log_config.radioLogger.error("No connection")
				return False
			with socketConn:
				while True:
					if not self.check_subprocess():
						return self.check_is_running()
					#don't want to wait for 'next' signal from ices when it
					#hasn't had anything to process
					if not skipped:
						res = socketConn.recv(1)
						if res == b"0" or res == b"":
							log_config.radioLogger.info("zero or blank signal sent from ices")
							return self.check_is_running()
						elif res == b"2":
							res = socketConn.recv(1)
							if res == b"0" or res == b"":
								log_config.radioLogger.info("zero or blank signal sent from ices")
								return self.check_is_running()
							#previously loaded
							if self.currentFile:
								self.send_next(socketConn)
								continue
					self.close_current_file()
					with self.fileQueue.delayed_decrement_get(
						lambda _: self.check_is_running()
					) as (currentFile, queueItem):
						skipped = not self.set_current_song(currentFile, queueItem)
						if skipped:
							continue
					if not self.send_next(socketConn):
						break
			return self.check_is_running()
		except Exception as e:
			if isinstance(e, TimeoutError) and not self.check_is_running():
				log_config.radioLogger.warning(e, exc_info=True)
				log_config.radioLogger.debug("Queue has stopped waiting on get")
				return False
			log_config.radioLogger.error(e, exc_info=True)
			return False
		finally:
			self.cleanup_socket(listener)
			self.clean_up_ices_process()


