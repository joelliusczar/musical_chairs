from sqlalchemy import select, desc
from musical_chairs_libs.tables import stations_history, songs, stations, \
	albums, artists, song_artist


def get_history_for_station(conn, 
stationName, 
limit=50, 
offset=0):
	h = stations_history.c
	st = stations.c
	sg = songs.c
	ab = albums.c
	ar = artists.c
	sgar = song_artist.c
	query = select(sg.pk, sg.path, h.playedTimestamp, sg.title, ab.name.label("album"),\
		ar.name.label("artist")) \
		.select_from(stations_history) \
		.join(songs, h.songFK == sg.pk) \
		.join(stations, st.pk == h.stationFK) \
		.join(albums, sg.albumFk == ab.pk, isouter=True) \
		.join(song_artist, sg.pk == sgar.songFk, isouter=True) \
		.join(artists, sgar.artistFk == ar.pk, isouter=True) \
		.where(st.name == stationName) \
		.order_by(desc(h.playedTimestamp)) \
		.limit(limit)
	records = conn.execute(query)
	for row in records:
		yield { 
				'id': row.pk,
				'song': row.title, 
				'album': row.album,
				'artist': row.artist,
				'playedTimestamp': row.playedTimestamp,
		}