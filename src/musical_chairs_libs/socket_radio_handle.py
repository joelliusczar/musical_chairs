import socket
import sys
import os


class SocketRadioHandle:

	def __init__(self) -> None:
		self.songnumber = -1
		self.songFullPath = ""
		self.display = ""
		self.client = None


	def ices_init(self) -> int:
		print('Executing initialize() function..')
		return 1

	# Function called to shutdown your python enviroment.
	# Return 1 if ok, 0 if something went wrong.
	def ices_shutdown(self) -> int:
		print(f"Station is shutting down on {self.display}")
		print(self.songFullPath)
		if self.client:
			try:
				self.client.sendall(b"0")
			except Exception:
				sys.stderr.write("Listener is closed while shutting down?\n")
			self.client.close()
		print('Executing shutdown() function...')
		return 1

	# Function called to get the next filename to stream.
	# Should return a string.
	def ices_get_next(self) -> str:
		if not self.client:
			host = "127.0.0.1"
			portNumber = int(os.environ["MC_STATION_PORT"])
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client.connect((host, portNumber))
		try:
			self.client.sendall(b"1")
		except Exception:
			sys.stderr.write("Listener is closed?\n")
			return ""
		sockfile = socket.SocketIO(self.client, "r")
		songFullPath = None
		display = None
		try:
			songFullPath = sockfile.readline()
			display = sockfile.readline()
			self.songFullPath = songFullPath.rstrip(b"\n").decode()
			self.display = display.rstrip(b"\n").decode()
			print(f"recieved display {self.display}")
			print(f"recieved full path {self.songFullPath}")
			return self.songFullPath
		except:
			print("Error")
			print(songFullPath)
			print(display)
			raise

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