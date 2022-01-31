from sqlalchemy import create_engine
from musical_chairs_libs.queue_manager import get_next_queued
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.station_manager import set_station_proc, remove_station_proc



class RadioHandle:

	def __init__(self, stationName):
		self.songnumber = -1
		self.songFullPath = ""
		self.display = ""
		self.config = get_config()
		self.stationName = stationName

	def ices_init(self):
		dbName = self.config['dbName']
		engine = create_engine(f"sqlite+pysqlite:///{dbName}")
		conn = engine.connect()
		set_station_proc(conn, self.stationName)
		conn.close()
		print('Executing initialize() function..')
		return 1

	# Function called to shutdown your python enviroment.
	# Return 1 if ok, 0 if something went wrong.
	def ices_shutdown(self):
		dbName = self.config['dbName']
		engine = create_engine(f"sqlite+pysqlite:///{dbName}")
		conn = engine.connect()
		remove_station_proc(conn, self.stationName)
		conn.close()
		print(f"Station is shutting down on {self.display}")
		print(self.songFullPath)
		print('Executing shutdown() function...')
		return 1

	# Function called to get the next filename to stream. 
	# Should return a string.
	def ices_get_next(self):
		searchBase = self.config['searchBase']
		dbName = self.config['dbName']
		engine = create_engine(f"sqlite+pysqlite:///{dbName}")
		conn = engine.connect()
		(currentsong, title, album, artist) = \
			get_next_queued(conn, self.stationName)
		conn.close()
		self.display = f"{title} - {album} - {artist}"
		self.songFullPath = f"{searchBase}/{currentsong}"
		return self.songFullPath

	# This function, if defined, returns the string you'd like used
	# as metadata (ie for title streaming) for the current song. You may
	# return null to indicate that the file comment should be used.
	def ices_get_metadata(self):
		return self.display

	# Function used to put the current line number of
	# the playlist in the cue file. If you don't care about this number
	# don't use it.
	def ices_get_lineno(self):
		print('Executing get_lineno() function...')
		self.songnumber = self.songnumber + 1
		return self.songnumber