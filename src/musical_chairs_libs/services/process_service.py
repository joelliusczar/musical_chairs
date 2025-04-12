import os
import platform
import subprocess
import random
from enum import Enum
from itertools import dropwhile, islice
from typing import Optional
from musical_chairs_libs.dtos_and_utilities import (
	get_non_simple_chars
)
from .env_manager import EnvManager
import musical_chairs_libs.dtos_and_utilities.logging as logging


class PackageManagers(Enum):
	APTGET = "apt-get"
	PACMAN = "pacman"
	HOMEBREW = "homebrew"


def __start_ices__(
	stationConf: str,
	portNumber: str
) -> subprocess.Popen[bytes]:
	if not os.path.isfile(stationConf):
		raise LookupError(f"Station conf not found at: {stationConf}")
	return subprocess.Popen(
		["mc-ices", "-c", f"{stationConf}"],
		env={
				"MCR_STATION_PORT": portNumber,
			 "PATH": os.environ["PATH"],
			 "LANG": os.environ["LANG"],
			 "MCR_CONTENT_HOME": EnvManager.relative_content_home(),
			 "MCR_APP_ROOT": EnvManager.app_root(),
			 "MCR_DB_PASS_RADIO": EnvManager.db_pass_radio(),
			 "MCR_RADIO_LOG_DIR_CL": EnvManager.radio_logs_dir(),
			 "MCR_DATABASE_NAME": EnvManager.db_name()
			}
	)


class ProcessService:

	stream_timeout = 5

	@staticmethod
	def noop_mode() -> bool:
		#the radio process deosn't currently on macs
		return platform.system() == "Darwin"

	@staticmethod
	def get_pid() -> int:
		if ProcessService.noop_mode():
			return random.randint(0, 1000)
		return os.getpid()

	@staticmethod
	def end_process(procId: int) -> None:
		if ProcessService.noop_mode():
			logging.radioLogger.info("Process service is using noop mode")
			return
		try:
			logging.radioLogger.info(f"Sending signal to end process {procId}")
			os.kill(procId, 15)
		except Exception as ex:
			logging.radioLogger.warn("Encountered issue when killing process")
			logging.radioLogger.warn(ex)

	@staticmethod
	def start_station_mc_ices(
		stationName: str,
		ownerName: str,
		portNumber: str
	) -> subprocess.Popen[bytes]:
		filename_base = f"{ownerName}_{stationName}"
		m = get_non_simple_chars(filename_base)
		if m:
			raise RuntimeError("Invalid station name was used")
		stationConf = f"{EnvManager.station_config_dir()}/ices.{filename_base}.conf"
		if ProcessService.noop_mode():
			print(
				"Noop mode. Won't search for station config"
	 			" nor try to launch process"
			)
			return #pyright: ignore [reportReturnType]
		return __start_ices__(stationConf, portNumber)

	@staticmethod
	def start_song_queue_process(dbName: str, stationName: str, ownerName: str):
		stationProc = subprocess.Popen([
				"python",
				"-m",
				"musical_chairs_libs.stream",
				dbName,
				stationName,
				ownerName
			],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
			stdin=subprocess.DEVNULL
		)

		try:
			stationProc.wait(ProcessService.stream_timeout)
			raise RuntimeError("Station ended sooner than expected")
		except subprocess.TimeoutExpired:
			logging.radioLogger.info("so far so good")



	@staticmethod
	def get_pkg_mgr() -> Optional[PackageManagers]:
		if platform.system() == "Linux":
			result = subprocess.run(
				["which", PackageManagers.PACMAN.value],
				stdout=subprocess.DEVNULL
			)
			if result.returncode == 0:
				return PackageManagers.PACMAN
			result = subprocess.run(
				["which", PackageManagers.APTGET.value],
				stdout=subprocess.DEVNULL
			)
			if result.returncode == 0:
				return PackageManagers.APTGET
		elif platform.system() == "Darwin":
			return PackageManagers.HOMEBREW
		return None

	@staticmethod
	def get_icecast_name() -> str:
		packageManager = ProcessService.get_pkg_mgr()
		if packageManager == PackageManagers.PACMAN:
			return "icecast"
		return "icecast2"

	@staticmethod
	def get_icecast_conf_location() -> str:
		icecastName = ProcessService.get_icecast_name()
		if platform.system() == "Linux":
			result = subprocess.run(
				["systemctl", "status", icecastName],
				capture_output=True,
				text=True
			)
			if result.returncode != 0:
				raise RuntimeError(f"{icecastName} is not running at the moment")
			relevantLine = next(islice(dropwhile(
				lambda l: "CGroup" not in l,
				result.stdout.split("\n")
			), 1, 2)).split()
			if relevantLine:
				return relevantLine[-1]
			else:
				raise RuntimeError("Was unable to determine icecast config location")
		elif platform.system() == "Darwin":
			#we don't have icecast on the mac anyway so we'll just return the
			#source code location
			return f"{EnvManager.templates_dir()}/icecast.xml"
		err = "icecast logic has not been configured for this os"
		raise NotImplementedError(err)
