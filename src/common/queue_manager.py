#!/usr/bin/env python2
from numpy.random import choice
import time
from tinytag import TinyTag

def get_station_pk(conn, stationName):
    cursor = conn.cursor()
    n = (stationName, )
    cursor.execute("SELECT [PK] FROM [Stations] WHERE Name = ?", n)
    row = cursor.fetchone()
    pk = row[0] if row else None
    cursor.close()
    return pk

def get_tag_pk(conn, tagName):
    cursor = conn.cursor()
    n = (tagName, )
    cursor.execute("SELECT [PK] FROM [Tags] WHERE Name = ?", n)
    row = cursor.fetchone()
    pk = row[0] if row else None
    cursor.close()
    return pk

def get_all_station_possibilities(conn, stationPk):

    cursor = conn.cursor()
    params = (stationPk, )

    cursor.execute("SELECT SG.[PK], SG.[Path]"
        "FROM [Stations] S "
        "JOIN [StationsTags] ST ON S.[PK] = ST.[StationFK] "
        "JOIN [SongsTags] SGT ON SGT.[TagFK] = ST.[TagFK] "
        "JOIN [Songs] SG ON SG.[PK] = SGT.[SongFK] "
        "LEFT JOIN [StationHistory] SH ON SH.[StationFK] = S.[PK] "
        "   AND SH.[SongFK] = SG.[PK] "
        "WHERE S.[PK] = ? AND (SGT.[Skip] IS NULL OR SGT.[Skip] = 0) "
        "GROUP BY SG.[PK]"
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
            "([StationFK], [SongFK], [LastPlayedTimestamp], "
            "[LastRequestedTimestamp]) "
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
    cursor.execute("SELECT S.[PK], S.[Path], S.[Title], S.[Album], "
        "S.[Artist], Q.[AddedTimestamp], Q.[RequestedTimestamp] "
        "FROM [StationQueue] Q "
        "JOIN [Songs] S ON Q.[SongFK] = S.[PK] "
        "WHERE Q.[StationFK] = ?"
        "ORDER BY [AddedTimestamp] ASC "
        "LIMIT 1", params)
    (songPk, path, title, album, artist, \
        queueTimestamp, requestedTimestamp) = cursor.fetchone()
    cursor.close()
    move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp, requestedTimestamp)
    fil_up_queue(conn, stationPk, queueSize)
    conn.commit()
    return (path, title, album, artist)




    