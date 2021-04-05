import sys
import sqlite3
from musical_chairs_libs.config_loader import get_config

def get_songs_by_path(conn, pathSegment = '', pageNum = 0):
    cursor = conn.cursor()
    wildCardSegment = '%s%%' % pathSegment
    skip = 50 * pageNum

    params = (wildCardSegment, skip, )
    cursor.execute("SELECT [SongPK], [Path] FROM [Songs] "
        "WHERE [PATH] LIKE ? "
        "ORDER BY [Path] "
        "LIMIT ?, 50",params)
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        yield '%d: %s' % (row[0], row[1])

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    arg1 = sys.argv[1] if len(sys.argv) > 1 else ''
    arg2 = sys.argv[2] if len(sys.argv) > 2 else 0
    results = get_songs_by_path(conn, arg1, arg2)
    for res in results:
        print(res)
    conn.close()