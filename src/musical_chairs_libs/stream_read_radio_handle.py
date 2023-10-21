import sys



class StreamReadRadioHandle:

	def __init__(self) -> None:
		self.songnumber = -1
		self.songFullPath = ""


	def ices_init(self) -> int:
		print('Executing initialize() function..')
		return 1

	# Function called to shutdown your python enviroment.
	# Return 1 if ok, 0 if something went wrong.
	def ices_shutdown(self) -> int:
		print(f"Station is shutting down on {self.display}")
		print(self.songFullPath)
		print('Executing shutdown() function...')
		return 1

	# Function called to get the next filename to stream.
	# Should return a string.
	def ices_get_next(self) -> str:
		self.display = sys.stdin.buffer.readline().decode()
		self.songFullPath = sys.stdin.buffer.readline().decode()
		print(f"recieved display {self.display}")
		print(f"recieved full path {self.songFullPath}")
		return ">"

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