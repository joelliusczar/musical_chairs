import sys
import yaml
import os
import sqlite3
from tinytag import TinyTag
from queue_manager import get_next_queued

# This is just a skeleton, something for you to start with.

songnumber = -1
songFullPath = ''
config = None
stationName = 'vg'

# Function called to initialize your python environment.
# Should return 1 if ok, and 0 if something went wrong.
def ices_init ():
	global config
	configPath = ''
	if 'radio_config' in os.environ:
		configPath = os.environ['radio_config']
	else:
		configPath = 'src/configs/config.yml'

	with open(configPath,'r') as stream:
		config =  yaml.safe_load(stream)
	print('Process Id: %d' % os.getpid())
	print('Executing initialize() function..')
	return 1

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
def ices_shutdown ():
	print('Executing shutdown() function...')
	return 1

# Function called to get the next filename to stream. 
# Should return a string.
def ices_get_next ():
	global songFullPath
	global stationName
	global config
	searchBase = config['searchBase']
	dbName = config['dbName']
	conn = sqlite3.connect(dbName)
	currentsong = get_next_queued(conn, stationName)
	conn.close()
	songFullPath = (searchBase + "/" + currentsong).encode('utf-8')
	return songFullPath

# This function, if defined, returns the string you'd like used
# as metadata (ie for title streaming) for the current song. You may
# return null to indicate that the file comment should be used.
def ices_get_metadata ():
	global songFullPath
	tag = TinyTag.get(songFullPath)
	metadataStr = None
	if not tag.artist and not tag.album:
		return tag.title
	if not tag.album:
		metadataStr = '%s - %s' % (tag.title, tag.artist)
	if not tag.artist:
		metadataStr = '%s - %s' % (tag.title, tag.artist)
	metadataStr = '%s - %s - %s' % (tag.title, tag.artist, tag.album)
	return metadataStr

# Function used to put the current line number of
# the playlist in the cue file. If you don't care about this number
# don't use it.
def ices_get_lineno ():
	global songnumber
	print('Executing get_lineno() function...')
	songnumber = songnumber + 1
	return songnumber