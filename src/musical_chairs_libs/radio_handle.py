#pyright: reportMissingTypeStubs=false
import os
from typing import Optional
from musical_chairs_libs.services import (
	EnvManager,
	QueueService,
	StationService
)



class RadioHandle:

	def __init__(
		self,
		stationId: int,
		dbName: str,
		envManager: Optional[EnvManager]=None
	) -> None:
		self.dbName = dbName
		self.songnumber = -1
		self.songFullPath = ""
		self.display = ""
		if not envManager:
			envManager = EnvManager()
		self.env_manager = envManager
		self.stationId = stationId

	def ices_init(self) -> int:
		conn = self.env_manager.get_configured_radio_connection(self.dbName)
		StationService(conn)\
			.set_station_proc(stationId=self.stationId)
		conn.commit()
		conn.close()
		print('Executing initialize() function..')
		return 1

	# Function called to shutdown your python enviroment.
	# Return 1 if ok, 0 if something went wrong.
	def ices_shutdown(self) -> int:
		conn = self.env_manager.get_configured_radio_connection(self.dbName)
		StationService(conn)\
			.unset_station_procs(stationIds=self.stationId)
		conn.commit()
		conn.close()
		print(f"Station is shutting down on {self.display}")
		print(self.songFullPath)
		print('Executing shutdown() function...')
		return 1

	# Function called to get the next filename to stream.
	# Should return a string.
	def ices_get_next(self) -> str:
		searchBase = EnvManager.absolute_content_home()
		conn = self.env_manager.get_configured_radio_connection(self.dbName)
		queueService = QueueService(conn)
		(songPath, songName, album, artist) = \
			queueService.pop_next_queued(stationId=self.stationId)
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