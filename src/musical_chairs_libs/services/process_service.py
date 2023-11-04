import os
import platform
import subprocess
import random
from pathlib import Path
from enum import Enum
from itertools import dropwhile, islice
from typing import Optional
from musical_chairs_libs.dtos_and_utilities import (
	get_non_simple_chars
)
from .env_manager import EnvManager

class PackageManagers(Enum):
	APTGET = "apt-get"
	PACMAN = "pacman"
	HOMEBREW = "homebrew"


def __start_ices__(stationConf: str):
	subprocess.run(["mc-ices", "-c", f"{stationConf}", "-B"])

def __create_missing_directories__(fullPath: str):
		path = Path(fullPath)
		if not path.parents[0].exists():
			path.parents[0].mkdir(parents=True, exist_ok=True)


class ProcessService:

	@staticmethod
	def noop_mode() -> bool:
		return platform.system() == "Darwin"

	@staticmethod
	def get_pid() -> int:
		if ProcessService.noop_mode():
			return random.randint(0, 1000)
		return os.getpid()

	@staticmethod
	def end_process(procId: int) -> None:
		if ProcessService.noop_mode():
			return
		try:
			os.kill(procId, 15)
		except:
			pass

	@staticmethod
	def start_station_external_process(
		stationName: str,
		ownerName: str
	) -> None:
		filename_base = f"{ownerName}_{stationName}"
		m = get_non_simple_chars(filename_base)
		if m:
			raise RuntimeError("Invalid station name was used")
		stationConf = f"{EnvManager.station_config_dir}/ices.{filename_base}.conf"
		if ProcessService.noop_mode():
			print(
				"Noop mode. Won't search for station config"
	 			" nor try to launch process"
			)
			return
		if not os.path.isfile(stationConf):
			raise LookupError(f"Station not found at: {stationConf}")
		__start_ices__(stationConf)

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
			return f"{EnvManager.templates_dir}/icecast.xml"
		err = "icecast logic has not been configured for this os"
		raise NotImplementedError(err)

