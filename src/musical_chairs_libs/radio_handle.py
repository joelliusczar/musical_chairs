import os
from fastapi import Depends
from musical_chairs_libs.dependencies import \
station_service, \
queue_service


class RadioHandle:

	def __init__(self, stationName: str) -> None:
		self.songnumber = -1
		self.songFullPath = ""
		self.display = ""
		self.stationName = stationName

	def ices_init(self) -> int:
		Depends(station_service).set_station_proc(self.stationName)
		print('Executing initialize() function..')
		return 1

	# Function called to shutdown your python enviroment.
	# Return 1 if ok, 0 if something went wrong.
	def ices_shutdown(self) -> int:
		Depends(station_service).remove_station_proc(self.stationName)
		print(f"Station is shutting down on {self.display}")
		print(self.songFullPath)
		print('Executing shutdown() function...')
		return 1

	# Function called to get the next filename to stream. 
	# Should return a string.
	def ices_get_next(self) -> str:
		searchBase = self.config_loader.config['searchBase']
		queueService = Depends(queue_service)
		(songPath, title, album, artist) = \
			queueService.pop_next_queued(self.stationName)
		if title:
			self.display = f"{title} - {album} - {artist}"
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