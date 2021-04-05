import sys
import sqlite3
from musical_chairs_libs.queue_manager import get_tag_pk

def delete_from_tag(conn, songPk, tagName):
    tagPk = get_tag_pk(conn, tagName)
    cursor = conn.cursor()
    params = (songPk, tagPk, )
    cursor.except('DELETE FROM [SongsTags] WHERE [SongFK] = ? AND [TagFK] = ?', params)
    cursor.close()

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    delete_from_tag(conn, sys.argv[1], sys.argv[2])
    conn.commit()
    conn.close()
