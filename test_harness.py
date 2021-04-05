import sys
import sqlite3
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_manager import get_all_station_possibilities
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
    # add_to_tag(conn, 1840, 'thinking')
    #    "FROM [Stations] S "
    #     "JOIN [StationsTags] ST ON S.[StationPK] = ST.[StationFK] "
    #     "JOIN [SongsTags] SGT ON SGT.[TagFK] = ST.[TagFK] "
    #     "JOIN [Songs] SG ON SG.[SongPK] = SGT.[SongFK] "
    #     "LEFT JOIN (SELECT [StationFK], MAX([LastPlayedTimestamp]), [SongFK] "
    #     "   FROM [StationHstory]"
    #     ") SH ON SH.[StationFK] = S.[StationPK] "
    #         "   AND SH.[SongFK] = SG.[SongPK] "
    #     "WHERE S.[StationPK] = ? ",
    cursor = conn.cursor()
    params = (3, )
    cursor.execute("SELECT SG.[SongPK], SG.[Path], MAX(SH.[LastPlayedTimestamp]) "
        "FROM [Stations] S "
        "JOIN [StationsTags] ST ON S.[StationPK] = ST.[StationFK] "
        "JOIN [SongsTags] SGT ON SGT.[TagFK] = ST.[TagFK] "
        "JOIN [Songs] SG ON SG.[SongPK] = SGT.[SongFK] "
        "LEFT JOIN [StationHistory] SH ON SH.[StationFK] = S.[StationPK] "
        "   AND SH.[SongFK] = SG.[SongPK] "
        "WHERE S.[StationPK] = ? AND (SGT.[Skip] IS NULL OR SGT.[Skip] = 0) "
        "GROUP BY SG.[SongPK], SG.[Path] "
        "ORDER BY SH.[LastPlayedTimestamp] DESC "
        , params)
    # cursor.execute("SELECT SG.[SongPK], SG.[Path], SH.[LastPlayedTimestamp] "
    #     "FROM [Stations] S "
    #     "JOIN [StationsTags] ST ON S.[StationPK] = ST.[StationFK] "
    #     "JOIN [SongsTags] SGT ON SGT.[TagFK] = ST.[TagFK] "
    #     "JOIN [Songs] SG ON SG.[SongPK] = SGT.[SongFK] "
    #     "LEFT JOIN [StationHistory] SH ON SH.[StationFK] = S.[StationPK] "
    #     "   AND SH.[SongFK] = SG.[SongPK]"
    #     "WHERE S.[StationPK] = ? AND (SGT.[Skip] IS NULL OR SGT.[Skip] = 0) "
    #     "ORDER BY SH.[LastPlayedTimestamp] DESC "
    #     , params)
    rows = cursor.fetchall()
    print(len(rows))
    for row in rows:
        print(row)
    conn.commit()
    conn.close()
