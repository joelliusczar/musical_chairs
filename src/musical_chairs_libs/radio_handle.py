#pyright: reportMissingTypeStubs=false
import os
from typing import Optional
from musical_chairs_libs.services import\
	EnvManager,\
	QueueService,\
	StationService
from musical_chairs_libs.dtos_and_utilities import OSProcessManager



class RadioHandle:

	def __init__(
		self,
		stationName: str,
		envManager: Optional[EnvManager]=None,
		processManager: Optional[OSProcessManager]=None
	) -> None:
		self.songnumber = -1
		self.songFullPath = ""
		self.display = ""
		if not envManager:
			envManager = EnvManager()
		if not processManager:
			processManager = OSProcessManager()
		self.env_manager = envManager
		self.stationName = stationName
		self.process_manager = processManager

	def ices_init(self) -> int:
		conn = self.env_manager.get_configured_db_connection()
		StationService(conn, processManager=self.process_manager)\
			.set_station_proc(stationName=self.stationName)
		conn.close()
		print('Executing initialize() function..')
		return 1

	# Function called to shutdown your python enviroment.
	# Return 1 if ok, 0 if something went wrong.
	def ices_shutdown(self) -> int:
		conn = self.env_manager.get_configured_db_connection()
		StationService(conn, processManager=self.process_manager)\
			.remove_station_proc(stationName=self.stationName)
		conn.close()
		print(f"Station is shutting down on {self.display}")
		print(self.songFullPath)
		print('Executing shutdown() function...')
		return 1

	# Function called to get the next filename to stream.
	# Should return a string.
	def ices_get_next(self) -> str:
		searchBase = self.env_manager.search_base
		conn = self.env_manager.get_configured_db_connection()
		queueService = QueueService(conn)
		(songPath, songName, album, artist) = \
			queueService.pop_next_queued(stationName=self.stationName)
		conn.close()
		if songName:
			self.display = f"{songName} - {album} - {artist}"
		else:
			self.display = os.path.splitext(os.path.split(songPath)[1])[0]
		self.songFullPath = f"{searchBase}/{songPath}"
		return self.songFullPath

	# This function, if defined, returns the string you'd like used
	# as metadata (ie for title streaming) for the current song. You may
	# return null to indicate that the file comment should be used.
	def ices_get_metadata(self) -> str:
		return self.display

	# Function used to put the current line number of
	# the playlist in the cue file. If you don't care about this number
	# don't use it.
	def ices_get_lineno(self) -> int:
		print('Executing get_lineno() function...')
		self.songnumber = self.songnumber + 1
		return self.songnumber