from musical_chairs_libs.socket_radio_handle import SocketRadioHandle
from typing import Optional

handle: Optional[SocketRadioHandle] = None #pyright: ignore [reportGeneralTypeIssues]

# Function called to initialize your python environment.
# Should return 1 if ok, and 0 if something went wrong.
def ices_init():
	global handle
	handle = SocketRadioHandle()
	return handle.ices_init()

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
def ices_shutdown():
	global handle
	if handle:
		return handle.ices_shutdown()
	print("Radio sub handle is missing in ices_shutdown")
	return 0

# Function called to get the next filename to stream.
# Should return a string.
def ices_get_next():
	global handle
	if handle:
		return handle.ices_get_next()
	print("Radio sub handle is missing in ices_get_next")
	return ""


# This function, if defined, returns the string you'd like used
# as metadata (ie for title streaming) for the current song. You may
# return null to indicate that the file comment should be used.
def ices_get_metadata():
	global handle
	if handle:
		return handle.ices_get_metadata()
	print("Radio sub handle is missing in ices_get_metadata")
	return ""

# Function used to put the current line number of
# the playlist in the cue file. If you don't care about this number
# don't use it.
def ices_get_lineno():
	global handle
	if handle:
		return handle.ices_get_lineno()
	print("Radio sub handle is missing in ices_get_lineno")
	return -1