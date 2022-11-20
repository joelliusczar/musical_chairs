import os
import platform
import subprocess
from musical_chairs_libs.dtos_and_utilities import check_name_safety
from .env_manager import EnvManager

class ProcessService:

	def getpid(self) -> int:
		return os.getpid()

	def end_process(self, procId: int) -> None:
		try:
			os.kill(procId, 15)
		except:
			pass

	def startup_station(self, stationName: str) -> None:
		m = check_name_safety(stationName)
		if m:
			raise RuntimeError("Invalid station name was used")
		if platform.system() == "Darwin":
			return
		stationConf = f"{EnvManager.station_config_dir}/{stationName}.conf"
		subprocess.run(["mc-ices", "-c", f"'{stationConf}'"])
