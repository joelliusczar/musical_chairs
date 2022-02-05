import sys
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_service import get_queue_for_station
import sqlite3


if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    for item in get_queue_for_station(conn, searchBase, sys.argv[1]):
        print(item)
    conn.close()