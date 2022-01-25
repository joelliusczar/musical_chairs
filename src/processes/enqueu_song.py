import sys
import sqlite3
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_manager import get_station_pk
import time

def enqueu_song(conn, songPk, stationName):
    tagPk = get_station_pk(stationName, conn)
    cursor = conn.cursor()
    timestamp = time.time()
    params = (songPk, tagPk, timestamp, timestamp, )
    cursor.execute("INSERT INTO [StationQueue] ([StationFK], [SongFK], "
        "[AddedTimestamp], [RequestedTimestamp]) VALUES(?, ?, ?, ?)", params)
    cursor.close()

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    enqueu_song(conn, sys.argv[1], sys.argv[2])
    conn.commit()
    conn.close()
