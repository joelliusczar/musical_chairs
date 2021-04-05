import sys
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_manager import get_queue_for_station


if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    conn = sqlite3.connect(dbName)
    for item in get_queue_for_station(conn, sys.argv[1]):
        print(item)
    conn.close()