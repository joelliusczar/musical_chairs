import sys
import sqlite3
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_manager import get_tag_pk

def mark_as_skip(conn, songPk, tagName):
    tagPk = get_tag_pk(conn, tagName)
    cursor = conn.cursor()
    params = (songPk, tagPk, )
    cursor.except("UPDATE [SongsTags] SET [Skip] = 1 "
        "WHERE [SongFK] = ? AND [TagFK] = ?", params)
    cursor.close()

def mark_as_skip_total(conn, songPk):
    cursor = conn.cursor()
    params = (songPk, )
    cursor.except("UPDATE [SongsTags] SET [Skip] = 1 "
        "WHERE [SongFK] = ?", params)
    cursor.close()

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    if sys.argv[2]:
        mark_as_skip(conn, sys.argv[1], sys.argv[2])
    else:
        mark_as_skip_total(conn, sys.argv[1])
    conn.commit()
    conn.close()
