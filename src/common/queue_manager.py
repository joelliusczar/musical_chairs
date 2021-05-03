from numpy.random import choice
import time
from tinytag import TinyTag

def get_station_pk(conn, stationName):
    cursor = conn.cursor()
    n = (stationName, )
    cursor.execute("SELECT [StationPK] FROM [Stations] WHERE Name = ?", n)
    pk = cursor.fetchone()[0]
    cursor.close()
    return pk

def get_tag_pk(conn, tagName):
    cursor = conn.cursor()
    n = (tagName, )
    cursor.execute("SELECT [TagPK] FROM [Tags] WHERE Name = ?", n)
    pk = cursor.fetchone()[0]
    cursor.close()
    return pk

def get_all_station_possibilities(conn, stationPk):

    cursor = conn.cursor()
    params = (stationPk, )

    cursor.execute("SELECT SG.[SongPK], SG.[Path]"
        "FROM [Stations] S "
        "JOIN [StationsTags] ST ON S.[StationPK] = ST.[StationFK] "
        "JOIN [SongsTags] SGT ON SGT.[TagFK] = ST.[TagFK] "
        "JOIN [Songs] SG ON SG.[SongPK] = SGT.[SongFK] "
        "LEFT JOIN [StationHistory] SH ON SH.[StationFK] = S.[StationPK] "
        "   AND SH.[SongFK] = SG.[SongPK] "
        "WHERE S.[StationPK] = ? AND (SGT.[Skip] IS NULL OR SGT.[Skip] = 0) "
        "GROUP BY SG.[SongPK]"
        "ORDER BY SH.[LastQueuedTimestamp] DESC, SH.[LastPlayedTimestamp] DESC "
        , params)
    
    rows = cursor.fetchall()
    cursor.close()
    return rows

def get_random_songPks(conn, stationPk, deficit):
    rows = get_all_station_possibilities(conn, stationPk)
    sampleSize = deficit if deficit < len(rows) else len(rows)
    aSize = len(rows)
    pSize = len(rows) + 1
    songPks = map(lambda r: r[0], rows)
    weights = [2 * (float(n) / (pSize * aSize)) for n in xrange(1, pSize)]
    selection = choice(songPks, sampleSize, p=weights, replace=False)
    return selection

def fil_up_queue(conn, stationPk, queueSize):
    cursor = conn.cursor()
    queueParams = (stationPk, )
    cursor.execute("SELECT COUNT(1) FROM [StationQueue] "
    "WHERE [StationFK] = ?", queueParams)
    count = cursor.fetchone()[0]
    cursor.close()
    deficit = queueSize - count
    if deficit < 1:
        return
    songPks = get_random_songPks(conn, stationPk, deficit)
    timestamp = time.time()
    params = map(lambda s: (stationPk, s, timestamp, ), songPks)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO [StationQueue] "
        "([StationFK], [SongFK], [AddedTimestamp]) VALUES(?, ?, ?)", params)
    cursor.close()
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO [StationHistory] "
        "([StationFK], [SongFK], [LastQueuedTimestamp]) VALUES(?, ?, ?)", params)
    cursor.close()

def move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp, requestedTimestamp):
    cursor = conn.cursor()
    params = (stationPk, songPk, queueTimestamp, )
    cursor.execute("DELETE FROM [StationQueue] "
        "WHERE [StationFK] = ? AND "
        "[SongFK] = ? AND "
        "[AddedTimestamp] = ? ", params)
    cursor.close()
    cursor = conn.cursor()
    params = { 'station': stationPk, 
        'song': songPk, 
        'currentTime': time.time(), 
        'requestTime': requestedTimestamp }
    prevChangsCount = conn.total_changes
    cursor.execute("DROP TABLE IF EXISTS temp.[lastHistory]; ")
    cursor.execute("CREATE TEMP TABLE [lastHistory] AS "
        "SELECT [SongFK], MAX([LastQueuedTimestamp]) [LastQueued] "
        "FROM [StationHistory] "
        "WHERE [StationFK] = :station "
        "GROUP BY [SongFK] "
        "HAVING [LastQueued] IS NOT NULL; ", params)

    cursor.execute("UPDATE [StationHistory] "
        "SET [LastPlayedTimestamp] = :currentTime "
        "WHERE [StationFK] = :station "
        "AND [SongFK] = :song "
        "AND [SongFK] IN "
        "(SELECT [SongFK] "
        "       FROM temp.[lastHistory]) "
        "AND [LastQueuedTimestamp] IN "
        "(SELECT [LastQueued] "
        "   FROM temp.[lastHistory]); ", params)
    cursor.execute("DROP TABLE IF EXISTS temp.[lastHistory]; ", params)
    cursor.close()
    if conn.total_changes == prevChangsCount:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO [StationHistory] "
            "([StationFK], [SongFK], [LastPlayedTimestamp], [LastRequestedTimestamp])"
            "VALUES(:station, :song, :currentTime, :requestTime)", params)
        cursor.close()

def is_queue_empty(conn, stationPk):
    cursor = conn.cursor()
    params = (stationPk, )
    cursor.execute("SELECT COUNT(1) FROM [StationQueue] "
        "WHERE [StationFK] = ?", params)
    isEmpty = cursor.fetchone()[0] < 1
    cursor.close()
    return isEmpty


def get_next_queued(conn, stationName):
    stationPk = get_station_pk(conn, stationName)
    queueSize = 50
    if is_queue_empty(conn, stationPk):
        fil_up_queue(conn, stationPk, queueSize + 1)
    cursor = conn.cursor()
    params = (stationPk, )
    cursor.execute("SELECT S.[SongPK], S.[Path], Q.[AddedTimestamp], Q.[RequestedTimestamp] "
        "FROM [StationQueue] Q "
        "JOIN [Songs] S ON Q.[SongFK] = S.[SongPK] "
        "WHERE Q.[StationFK] = ?"
        "ORDER BY [AddedTimestamp] ASC "
        "LIMIT 1", params)
    (songPk, path, queueTimestamp, requestedTimestamp) = cursor.fetchone()
    cursor.close()
    move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp, requestedTimestamp)
    fil_up_queue(conn, stationPk, queueSize)
    conn.commit()
    return path

def get_queue_for_station(conn, searchBase, stationName):
    stationPk = get_station_pk(conn, stationName)
    cursor = conn.cursor()
    params = (stationPk, )
    cursor.execute("SELECT S.[SongPK], S.[Path], "
        "Q.[AddedTimestamp], Q.[RequestedTimestamp] "
            "FROM [StationQueue] Q "
            "JOIN [Songs] S ON Q.[SongFK] = S.[SongPK] "
            "WHERE Q.[StationFK] = ?"
            "ORDER BY [AddedTimestamp] ASC ", params)
    rows = cursor.fetchall()
    cursor.close()
    for idx, row in enumerate(rows):
        songFullPath = (searchBase + "/" + row[1]).encode('utf-8')
        try:
            tag = TinyTag.get(songFullPath)
            yield { 
                'songPK': row[0],
                'song': tag.title, 
                'album': tag.album,
                'artist': tag.artist,
                'AddedTimestamp': row[2],
                'RequestedTimestamp': row[3]
            }
        except:
            yield { 
                'songPK': row[0],
                'AddedTimestamp': row[2],
                'RequestedTimestamp': row[3]
            }

def get_station_list(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT [StationPK], [Name]"
        "FROM [Stations]")
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        yield { StationPK: row[0], Name: row[1]}


def get_history_for_station(conn, searchBase, stationName, limit = 50):
    stationPk = get_station_pk(conn, stationName)
    cursor = conn.cursor()
    params = (stationPk, limit, )
    cursor.execute("SELECT S.[SongPK], S.[Path], H.[LastPlayedTimestamp] "
        "FROM [StationHistory] H "
        "JOIN [Songs] S ON H.[SongFK] = S.[SongPK] "
        "WHERE H.[StationFK] = ?"
        "ORDER BY [LastPlayedTimestamp] DESC "
        "LIMIT ? ", params)
    rows = cursor.fetchall()
    cursor.close()
    for idx, row in enumerate(rows):
        songFullPath = (searchBase + "/" + row[1]).encode('utf-8')
        try:
            tag = TinyTag.get(songFullPath)
            yield { 
                'songPK': row[0],
                'song': tag.title, 
                'album': tag.album,
                'artist': tag.artist,
                'LastPlayedTimestamp': row[2]
            }
        except:
            yield {
                'songPK': row[0],
                'LastPlayedTimestamp': row[2]
            }

    


    