from dataclasses import dataclass
from sqlalchemy import select, desc
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import stations_history, songs, stations, \
	albums, artists, song_artist

@dataclass
class HistoryItem:
	songPk: int
	title: str
	albums: str
	artist: str
	playedTimestamp: float

class HistoryService:

	def __init__(self, conn: Connection) -> None:
			self.conn = conn

def get_history_for_station(self, stationName: str, limit: int = 50, offset: int = 0):
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
	records = self.conn.execute(query)
	for row in records:
		yield HistoryItem( 
				row.pk,
				row.title, 
				row.album,
				row.artist,
				row.playedTimestamp
				)