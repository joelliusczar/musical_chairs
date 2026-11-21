import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.services as mcr
import os
import sys
import signal
import subprocess
import time
import typing
from . import queue_song_source
from . import song_broker_context
from typing import Any
from threading import Thread
from setproctitle import setproctitle
import musical_chairs_libs.dtos_and_utilities.log_config as log_config
from sqlalchemy.exc import OperationalError


class SignalHandlerFactory:

	def __init__(self, broker: queue_song_source.SongBroker) -> None:
		self.broker = broker

	def build_signal_handler(
		self,
		name: str
	) -> typing.Callable[[Any, Any], None]:
		def handler(sigNum: Any, frame: Any):
			log_config.radioLogger.info(f"Received {name} signal")
			self.broker.stop()
			self.broker.clean_up_ices_process()
		return handler


def start_ices(portNumber: str) -> subprocess.Popen[bytes]:
		try:
			setproctitle(
				f"MC Radio - {ownerName}_{stationName} at {portNumber}"
			)
		except Exception as e:
			log_config.radioLogger.info("Failed to rename process")
			log_config.radioLogger.info(e)
		log_config.radioLogger.info(
			f"Starting mc ices with {ownerName}_{stationName}"
		)
		return mcr.ProcessService.start_station_mc_ices(
			stationName,
			ownerName,
			portNumber
		)


def launch_loading(
	broker: queue_song_source.SongBroker,
	cleanup: typing.Callable[[], None]
):	
	try:
		broker.load_loop()
	finally:
		cleanup()

def try_shutdown_station(
	station: dtos.StationInfo,
	stationProcessService: mcr.StationProcessService
):
	log_config.radioLogger.info(
		f"Disabling the station: {station.decoded_id()}"
	)
	attempts = 0
	try:
		while True:
			try:
				stationProcessService.unset_station_procs(
					stationIds=station.decoded_id()
				)
				break
			except OperationalError:
				attempts += 1
				log_config.radioLogger.warning(f"Database error. Attempt: {attempts}")
				if attempts > 3:
					log_config.radioLogger.error(
						f"Retried {attempts} times to avoid database issue"
					)
					raise
	except Exception as ex:
		log_config.radioLogger.error("Error attempting to close station")
		log_config.radioLogger.error(ex, exc_info=True)


def launch_sending(
	broker: queue_song_source.SongBroker,
	cleanup: typing.Callable[[], None]
):
	
	try:
		restartsAllowed = 3
		while restartsAllowed >= 0:
			if not broker.send_loop(mcr.ProcessService.stream_timeout):
				break
			restartsAllowed -= 1
			if restartsAllowed >= 0:
				time.sleep(5 * (3 - restartsAllowed + 1))
			if not broker.check_is_running():
				break
	finally:
		cleanup()


def start_song_queue(dbName: str, stationName: str, ownerName: str):
	log_config.radioLogger.error("Starting the queue process")
	log_config.radioLogger.debug(f"Debug canary: {os.getcwd()}")

	with song_broker_context.SongBrokerContext(
		dbName,
		stationName,
		ownerName
	) as load_support:
		with song_broker_context.SongBrokerContext(
			dbName,
			stationName,
			ownerName
		) as send_support:

			station = load_support.station
	
			broker = queue_song_source.SongBroker(
				load_support.pick_song_popper(),
				send_support.pick_song_popper(),
				station,
				song_broker_context.file_service(),
				start_ices
			)
			signalHandlerFactory = SignalHandlerFactory(broker)

			def send_thread_cleanup():
				log_config.radioLogger.debug("send_thread_cleanup")
				broker.stop()
				broker.clean_up_tmp_files()
				broker.clean_up_ices_process()

			def load_thread_cleanup():
				broker.stop()
				

			loadThread = Thread(
				target=launch_loading,
				args=[broker, load_thread_cleanup],
			)
			sendThread = Thread(
				target=launch_sending,
				args=[broker, send_thread_cleanup]
			)

			load_support.stationProcessService.set_station_proc(station.decoded_id())
			signal.signal(
				signal.SIGINT, 
				signalHandlerFactory.build_signal_handler("keyboard")
			)
			signal.signal(
				signal.SIGTERM, 
				signalHandlerFactory.build_signal_handler("termination")
			)
			try:
				loadThread.start()
				sendThread.start()

				sendThread.join() #wait for clean up to finish
				loadThread.join()
				log_config.radioLogger.debug("Escaped the loop")


			finally:
				broker.close_current_file()
				try_shutdown_station(station, load_support.stationProcessService)
				log_config.radioLogger.debug(
					f"Is loading thread alive? {loadThread.is_alive()}"
				)
				log_config.radioLogger.debug(
					f"Is sending thread alive? {sendThread.is_alive()}"
				)
				signal.signal(signal.SIGINT, signal.SIG_DFL)
				signal.signal(signal.SIGTERM, signal.SIG_DFL)



if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]

	try:
		start_song_queue(dbName, stationName, ownerName)
	except Exception as e:
		log_config.radioLogger.error(e, exc_info=True)
	log_config.radioLogger.info("End of station queue process")