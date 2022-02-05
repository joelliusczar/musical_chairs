import sys
import sqlite3
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_service import get_tag_pk

def add_to_tag(conn, songPk, tagName):
    tagPk = get_tag_pk(conn, tagName)
    cursor = conn.cursor()
    params = (songPk, tagPk, )
    cursor.execute("INSERT INTO [SongsTags] ([SongFK],[TagFK]) VALUES(?, ?)", params)
    cursor.close()

if __name__ == '__main__':
    config = get_config()
    dbName = config['dbName']
    searchBase = config['searchBase']
    conn = sqlite3.connect(dbName)
    add_to_tag(conn, sys.argv[1], sys.argv[2])
    conn.commit()
    conn.close()
