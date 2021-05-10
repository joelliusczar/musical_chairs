import sys
import yaml
import sqlite3
from musical_chairs_libs.queue_manager import get_next_queued
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.station_proc_manager import set_station_proc, remove_station_proc



class RadioHandle:

    def __init__(self, stationName):
        self.songnumber = -1
        self.songFullPath = ""
        self.display = ""
        self.config = get_config()
        self.stationName = stationName

    def ices_init(self):
        dbName = self.config['dbName']
        conn = sqlite3.connect(dbName)
        set_station_proc(conn, self.stationName)
        conn.commit()
        conn.close()
        print('Executing initialize() function..')
        return 1

    # Function called to shutdown your python enviroment.
    # Return 1 if ok, 0 if something went wrong.
    def ices_shutdown(self):
        dbName = self.config['dbName']
        conn = sqlite3.connect(dbName)
        remove_station_proc(conn, self.stationName)
        conn.commit()
        conn.close()
        print('Executing shutdown() function...')
        return 1

    # Function called to get the next filename to stream. 
    # Should return a string.
    def ices_get_next(self):
        searchBase = self.config['searchBase']
        dbName = self.config['dbName']
        conn = sqlite3.connect(dbName)
        (currentsong, title, album, artist) = \
            get_next_queued(conn, self.stationName)
        conn.close()
        self.display = "%s - %s - %s" % (title, artist, album)
        self.songFullPath = (searchBase + "/" + currentsong).encode('utf-8')
        return self.songFullPath

    # This function, if defined, returns the string you'd like used
    # as metadata (ie for title streaming) for the current song. You may
    # return null to indicate that the file comment should be used.
    def ices_get_metadata(self):
        return self.display.encode('utf-8')

    # Function used to put the current line number of
    # the playlist in the cue file. If you don't care about this number
    # don't use it.
    def ices_get_lineno(self):
        print('Executing get_lineno() function...')
        self.songnumber = self.songnumber + 1
        return self.songnumber