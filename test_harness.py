import sys
import sqlite3
from musical_chairs_libs.config_loader import get_config
from src.processes.get_songs_by_path import get_songs_by_path
from src.processes.add_to_tag import add_to_tag


if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    # arg1 = sys.argv[1] if len(sys.argv) > 1 else ''
    # arg2 = sys.argv[2] if len(sys.argv) > 2 else 0
    # results = get_songs_by_path(conn, arg1, arg2)
    # for res in results:
    #     print(res)
    add_to_tag(conn, 1840, 'thinking')
    conn.commit()
    conn.close()
