import sys
import sqlite3
from datetime import datetime
from tinytag import TinyTag
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.queue_manager import get_next_queued
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
    cursor.execute("SELECT S.[SongPK], S.[Path], MAX(SH.[LastPlayedTimestamp]), MAX(SH.[LastQueuedTimestamp]) [LastQueued] "
        "FROM [StationHistory] SH "
        "JOIN [Songs] S ON S.[SongPK] = SH.[SongFK] "
        "WHERE [StationFK] = ? "
        "GROUP BY S.[SongPK], S.[Path] "
        "HAVING [LastQueued] IS NOT NULL ", params)
    # cursor.executescript("DROP TABLE IF EXISTS temp.[lastHistory]; "
    #     "CREATE TEMP TABLE [lastHistory] AS "
    #     "SELECT [SongFK], MAX([LastQueuedTimestamp]) [LastQueued] "
    #     "FROM [StationHistory] "
    #     "WHERE [StationFK] = :station "
    #     "GROUP BY [SongFK]; "
    #     "UPDATE [StationHistory] "
    #     "SET [LastPlayedTimestamp] = :currentTime "
    #     "WHERE [StationFK] = :station "
    #     "AND [SongFK] = :song "
    #     "AND [SongFK] IN "
    #     "(SELECT [SongFK] "
    #     "       FROM temp.[lastHistory]) "
    #     "AND [LastQueuedTimestamp] IN "
    #     "(SELECT [LastQueued] "
    #     "   FROM temp.[lastHistory]); "
    #     "DROP TABLE IF EXISTS temp.[lastHistory]; ")
    rows = cursor.fetchall()
    pkDict = {}
    for row in rows:
        if row[0] in pkDict:
            pkDict[row[0]] += 1
        else:
            pkDict[row[0]] = 1
        print('%s - %s - LastPlayed: \033[94m%s\033[0m - LastQueue: %s' % (row[0], row[1], datetime.fromtimestamp(row[2]) if row[2] else 'Nope', datetime.fromtimestamp(row[3]) if row[3] else 'Nope' ))
    print(pkDict)
    print(len(rows))
    if len(filter(lambda x: x > 1, pkDict.values())):
        print('\033[93mWoah whoa \033[0m')
    path = get_next_queued(conn, 'thinking')
    print(path)
    conn.commit()
    conn.close()
