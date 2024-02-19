from musical_chairs_libs.radio_handle import RadioHandle
from musical_chairs_libs.services import EnvManager

handle: RadioHandle = None #pyright: ignore [reportAssignmentType]

# Function called to initialize your python environment.
# Should return 1 if ok, and 0 if something went wrong.
def ices_init():
	global handle
	dbName = EnvManager.db_name() #pyright: ignore
	handle = RadioHandle(<station_id>, dbName) #pyright: ignore
	return handle.ices_init()

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
def ices_shutdown():
	global handle
	return handle.ices_shutdown()

# Function called to get the next filename to stream.
# Should return a string.
def ices_get_next():
	global handle
	return handle.ices_get_next()


# This function, if defined, returns the string you'd like used
# as metadata (ie for title streaming) for the current song. You may
# return null to indicate that the file comment should be used.
def ices_get_metadata():
	global handle
	return handle.ices_get_metadata()

# Function used to put the current line number of
# the playlist in the cue file. If you don't care about this number
# don't use it.
def ices_get_lineno():
	global handle
	return handle.ices_get_lineno()