from dataclasses import dataclass
from sqlalchemy import select, desc
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import stations_history, songs, stations, \
	albums, artists, song_artist
from musical_chairs_libs.station_service import StationService

@dataclass
class HistoryItem:
	songPk: int
	title: str
	albums: str
	artist: str
	playedTimestamp: float

class HistoryService:

	def __init__(self, conn: Connection, stationService: StationService) -> None:
			self.conn = conn
			self.station_service = stationService

	def get_history_for_station(self, 
		stationPk: int=None,
		stationName: str=None, 
		limit: int=50, 
		offset: int=0
	):
		if not stationPk:
			if stationName:
				stationPk = self.station_service.get_station_pk(stationName)
			else:
				raise ValueError("Either stationName or pk must be provided")
		h = stations_history.c
		st = stations.c
		sg = songs.c
		ab = albums.c
		ar = artists.c
		sgar = song_artist.c
		query = select(
			sg.pk, \
			sg.path, \
			h.playedTimestamp, \
			sg.title, \
			ab.name.label("album"),\
			ar.name.label("artist")
		).select_from(stations_history) \
			.join(songs, h.songFk == sg.pk) \
			.join(stations, st.pk == h.stationFk) \
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