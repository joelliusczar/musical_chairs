from numpy.random import choice
import time
from sqlalchemy import select, desc, func, insert, delete, update
from musical_chairs_libs.tables import stations_history, songs, stations,\
     tags, stations_tags, songs_tags, station_queue, albums, artists, song_artist, \
    last_history_tmp


def get_station_pk(conn, stationName):
    st = stations.c
    query = select(st.pk) \
        .select_from(stations) \
        .where(st.name == stationName)
    row = conn.execute(query).fetchone()
    pk = row.pk if row else None
    return pk

def get_tag_pk(conn, tagName):
    t = tags.c
    query = select(t.pk) \
        .select_from(tags) \
        .where(t.name == tagName)
    row = conn.execute(query).fetchone()
    pk = row.pk if row else None
    return pk

def get_all_station_song_possibilities(conn, stationPk):
    st = stations.c
    sg = songs.c
    sttg = stations_tags.c
    sgtg = songs_tags.c
    hist = stations_history.c
    
    query = select(sg.pk, sg.path) \
        .select_from(stations) \
        .join(stations_tags, st.pk == sttg.stationFk) \
        .join(songs_tags, sgtg.tagFk == sttg.tagFk) \
        .join(songs, sg.pk == sgtg.songFk) \
        .join(stations_history, (hist.stationFk == st.pk) \
            & (hist.songFk == sg.pk), isouter=True) \
        .where(st.pk == stationPk) \
        .where((sgtg.skip == None) | (sgtg.skip == 0)) \
        .group_by(sg.pk, sg.path) \
        .order_by(desc(func.max(hist.lastQueuedTimestamp))) \
        .order_by(desc(func.max(hist.lastPlayedTimestamp)))
    
    rows = conn.execute(query).fetchall()
    return rows

def get_random_songPks(conn, stationPk, deficit):
    rows = get_all_station_song_possibilities(conn, stationPk)
    sampleSize = deficit if deficit < len(rows) else len(rows)
    aSize = len(rows)
    pSize = len(rows) + 1
    songPks = map(lambda r: r.pk, rows)
    # the sum of weights needs to equal 1
    weights = [2 * (float(n) / (pSize * aSize)) for n in range(1, pSize)]
    selection = choice(songPks, sampleSize, p = weights, replace=False)
    return selection

def fil_up_queue(conn, stationPk, queueSize):
    q = station_queue.c
    queryQueueSize = select(func.count(1)).select_from(station_queue)\
        .where(q.stationFk == stationPk)
    count = conn.execute(queryQueueSize).fetchone().count
    deficit = queueSize - count
    if deficit < 1:
        return
    songPks = get_random_songPks(conn, stationPk, deficit)
    timestamp = time.time()
    params = list(map(lambda s: {"stationFk": stationPk, "songFk": s, "addedTimestamp": timestamp }, songPks))
    queueInsert = insert(station_queue).values(params)
    conn.execute(queueInsert)
    historyInsert = insert(stations_history).values(params)
    conn.execute(historyInsert)

def move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp, requestedTimestamp):
    q = station_queue.c
    # can't delete by songPk alone b/c the song might be queued multiple times
    queueDel = delete(station_queue).where(q.stationFk == stationPk) \
        .where(q.songFk == songPk) \
        .where(q.addedTimestamp == queueTimestamp)
    delResult = conn.execute(queueDel)
    currentTime = time.time()

    prevChangsCount = delResult.rowcount

    last_history_tmp.drop(conn, checkfirst = True)
    last_history_tmp.create(conn)

    hist = stations_history.c
    lastQueued = func.max(hist.lastQueuedTimestamp).label("lastQueued")
    lastHistoryQuery = select(hist.songFk, lastQueued) \
        .select_from(stations_history) \
        .where(hist.stationFk == stationPk) \
        .group_by(hist.songFk) \
        .having(lastQueued != None)
    tmp = last_history_tmp.c
    tmpInsert = insert(last_history_tmp) \
        .from_select([tmp.songFk, tmp.lastQueued],lastHistoryQuery)
    conn.execute(tmpInsert)

    songTmpSubquery = select(tmp.songFk).select_from(last_history_tmp).subquery()
    tsTmpSubquery = select(tmp.lastQueued).select_from(last_history_tmp).subquery()
    histUpdateStmt = update(stations_history) \
        .values(lastPlayedTimestamp = currentTime) \
        .where(hist.stationFk == stationPk) \
        .where(hist.songFk == songPk) \
        .where(hist.songFk.in_(songTmpSubquery)) \
        .where(hist.lastQueuedTimestamp.in_(tsTmpSubquery))
    histUpdateResult = conn.execute(histUpdateStmt)
    last_history_tmp.drop(conn, checkfirst = True)

    if histUpdateResult.rowcount == prevChangsCount:
        histInsert = insert(stations_history) \
            .values(stationFk = stationPk, songFk = songPk, lastPlayedTimestamp = currentTime, \
                lastRequestedTimestamp = requestedTimestamp)
        conn.execute(histInsert)


def is_queue_empty(conn, stationPk):
    q = station_queue.c
    query = select(func.count(1)).select_from(station_queue).where(q.stationFk == stationPk)
    res = conn.execute(query).fetchone()
    return res.count < 1


def get_next_queued(conn, stationName, queueSize = 50):
    stationPk = get_station_pk(conn, stationName)
    if is_queue_empty(conn, stationPk):
        fil_up_queue(conn, stationPk, queueSize + 1)
    sg = songs.c
    q = station_queue.c
    ab = albums.c
    ar = artists.c
    sgar = song_artist.c
    query = select(sg.pk, sg.path, sg.title, ab.name, ar.name, \
        q.addedTimestamp, q.requestedTimestamp).select_from(station_queue) \
        .join(songs, sg.pk == q.songsFk) \
        .join(albums, sg.albumFk == ab.pk, isouter=True) \
        .join(song_artist, sg.pk == sgar.songFk, isouter=True) \
        .join(artists, ar.pk == sgar.artistFk) \
        .where(q.stationFk == stationPk) \
        .order_by(q.addedTimestamp) \
        .limit(1)
    (songPk, path, title, album, artist, \
        queueTimestamp, requestedTimestamp) = conn.execute(query).fetchone()
    move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp, requestedTimestamp)
    fil_up_queue(conn, stationPk, queueSize)
    conn.commit()
    return (path, title, album, artist)




    