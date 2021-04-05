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

def get_all_station_possibilities(conn, stationPk):

    cursor = conn.cursor()
    params = (stationPk, )

    cursor.execute("SELECT SG.[SongPK]"
        "FROM [Stations] S "
        "JOIN [StationsTags] ST ON S.[StationPK] = ST.[StationFK] "
        "JOIN [SongsTags] SGT ON SGT.[TagFK] = ST.[TagFK] "
        "JOIN [Songs] SG ON SG.[SongPK] = SGT.[SongFK] "
        "LEFT JOIN [StationHistory] SH ON SH.[StationFK] = S.[StationPK] "
        "   AND SH.[SongFK] = SG.[SongPK]"
        "WHERE S.[StationPK] = ? AND (SGT.[Skip] IS NULL OR SGT.[Skip] = 0) "
        "ORDER BY SH.[LastPlayedTimestamp] DESC"
        , params)
    
    rows = cursor.fetchall()
    cursor.close()
    return rows

def get_random_songPks(conn, stationPk, deficit):
    rows = get_all_station_possibilities(conn, stationPk)
    aSize = len(rows)
    pSize = len(rows) + 1
    songPks = map(lambda r: r[0], rows)
    weights = [2 * (float(n) / (pSize * aSize)) for n in xrange(1, pSize)]
    print(sum(weights))
    selection = choice(songPks, deficit, p=weights, replace=False)
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

def move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp, requestedTimestamp):
    cursor = conn.cursor()
    params = (stationPk, songPk, queueTimestamp, )
    cursor.execute("DELETE FROM [StationQueue] "
        "WHERE [StationFK] = ? AND "
        "[SongFK] = ? AND "
        "[AddedTimestamp] = ? ", params)
    cursor.close()
    cursor = conn.cursor()
    params = (stationPk, songPk, time.time(), requestedTimestamp, )
    cursor.execute("INSERT INTO [StationHistory] "
        "([StationFK], [SongFK], [LastPlayedTimestamp], [LastRequestedTimestamp])"
        "VALUES(?, ?, ?, ?)", params)
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

def get_queue_for_station(conn, stationName):
    stationPk = get_station_pk(conn, stationName)
    cursor = conn.cursor()
    params = (stationPk, )
    results = []
    cursor.execute("SELECT S.[SongPK], S.[Path], "
        "Q.[AddedTimestamp], Q.[RequestedTimestamp] "
            "FROM [StationQueue] Q "
            "JOIN [Songs] S ON Q.[SongFK] = S.[SongPK] "
            "WHERE Q.[StationFK] = ?"
            "ORDER BY [AddedTimestamp] ASC ", params)
    rows = cursor.fetchall()
    print(cursor.description)
    cursor.close()
    for idx, row in enumerate(rows):
        print(row)
        tag = TinyTag.get(row[1].encode('utf-8'))
        yield '%d: %s' % (idx, tag.title)



    


    