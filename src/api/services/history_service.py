from sqlalchemy import select, desc, func
from .tables import stations_history, songs, stations
from .sql_functions import song_name, album_name, artist_name


def get_history_for_station(conn, 
searchBase, 
stationName, 
limit=50, 
offset=0):
  h = stations_history.c
  st = stations.c
  s = songs.c
  query = select(s.songPK, s.path, h.lastPlayedTimestamp, \
    func.song_name(s.path, searchBase).label("songName"),\
    func.album_name(s.path, searchBase).label("albumName"),\
    func.artist_name(s.path, searchBase).label("artistName")) \
    .select_from(stations_history) \
    .join(songs, h.songFK == s.songPK) \
    .join(stations, st.stationPK == h.stationFK) \
    .where(st.name == stationName) \
    .order_by(desc(h.lastPlayedTimestamp)) \
    .limit(limit)
  records = conn.execute(query)
  for row in records:
    yield { 
        'id': row["songPK"],
        'song': row["songName"], 
        'album': row["albumName"],
        'artist': row["artistName"],
        'lastPlayedTimestamp': row["lastPlayedTimestamp"],
    }