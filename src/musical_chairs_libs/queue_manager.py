import time
from numpy.random import choice
from sqlalchemy import select, desc, func, insert, delete, update
from musical_chairs_libs.tables import stations_history, songs, stations,\
	 tags, stations_tags, songs_tags, station_queue, albums, artists, song_artist, \
	last_history_tmp
from musical_chairs_libs.station_manager import get_station_pk


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
		.order_by(desc(func.max(hist.queuedTimestamp))) \
		.order_by(desc(func.max(hist.playedTimestamp)))
	
	rows = conn.execute(query).fetchall()
	return rows

def get_random_songPks(conn, stationPk, deficit):
	rows = get_all_station_song_possibilities(conn, stationPk)
	sampleSize = deficit if deficit < len(rows) else len(rows)
	aSize = len(rows)
	pSize = len(rows) + 1
	songPks = list(map(lambda r: r.pk, rows))
	# the sum of weights needs to equal 1
	weights = [2 * (float(n) / (pSize * aSize)) for n in range(1, pSize)]
	selection = choice(songPks, sampleSize, p = weights, replace=False).tolist()
	return selection

def fil_up_queue(conn, stationPk, queueSize):
	q = station_queue.c
	queryQueueSize = select(func.count(1)).select_from(station_queue)\
		.where(q.stationFk == stationPk)
	count = conn.execute(queryQueueSize).scalar()
	deficit = queueSize - count
	if deficit < 1:
		return
	songPks = get_random_songPks(conn, stationPk, deficit)
	timestamp = time.time()
	params = list(map(lambda s: {"stationFk": stationPk, "songFk": s, "queuedTimestamp": timestamp }, songPks))
	queueInsert = insert(station_queue)
	conn.execute(queueInsert, params)
	historyInsert = insert(stations_history)
	conn.execute(historyInsert, params)

def move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp):
	q = station_queue.c
	# can't delete by songPk alone b/c the song might be queued multiple times
	queueDel = delete(station_queue).where(q.stationFk == stationPk) \
		.where(q.songFk == songPk) \
		.where(q.queuedTimestamp == queueTimestamp)
	conn.execute(queueDel)
	currentTime = time.time()

	hist = stations_history.c

	histUpdateStmt = update(stations_history) \
		.values(playedTimestamp = currentTime) \
		.where(hist.stationFk == stationPk) \
		.where(hist.songFk == songPk) \
		.where(hist.queuedTimestamp == queueTimestamp)
	conn.execute(histUpdateStmt)



def is_queue_empty(conn, stationPk):
	q = station_queue.c
	query = select(func.count(1)).select_from(station_queue).where(q.stationFk == stationPk)
	res = conn.execute(query).scalar()
	return res < 1


def get_next_queued(conn, stationName, queueSize = 50):
	stationPk = get_station_pk(stationName, conn)
	if is_queue_empty(conn, stationPk):
		fil_up_queue(conn, stationPk, queueSize + 1)
	sg = songs.c
	q = station_queue.c
	ab = albums.c
	ar = artists.c
	sgar = song_artist.c
	query = select(sg.pk, sg.path, sg.title, ab.name, ar.name, \
		q.queuedTimestamp).select_from(station_queue) \
		.join(songs, sg.pk == q.songFk) \
		.join(albums, sg.albumFk == ab.pk, isouter=True) \
		.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
		.join(artists, sgar.artistFk == ar.pk, isouter=True) \
		.where(q.stationFk == stationPk) \
		.order_by(q.queuedTimestamp) \
		.limit(1)
	(songPk, path, title, album, artist, \
		queueTimestamp) = conn.execute(query).fetchone()
	move_from_queue_to_history(conn, stationPk, songPk, queueTimestamp)
	fil_up_queue(conn, stationPk, queueSize)
	return (path, title, album, artist)




	