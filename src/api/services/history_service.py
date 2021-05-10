from sqlalchemy import select, desc, func
from .tables import stations_history, songs, stations
from .sql_functions import song_name, album_name, artist_name


def get_history_for_station(conn, 
stationName, 
limit=50, 
offset=0):
  h = stations_history.c
  st = stations.c
  s = songs.c
  query = select(s.pk, s.path, h.lastPlayedTimestamp, s.title, s.album,\
    s.artist) \
    .select_from(stations_history) \
    .join(songs, h.songFK == s.pk) \
    .join(stations, st.pk == h.stationFK) \
    .where(st.name == stationName) \
    .order_by(desc(h.lastPlayedTimestamp)) \
    .limit(limit)
  records = conn.execute(query)
  for row in records:
    yield { 
        'id': row[s.pk],
        'song': row[s.title], 
        'album': row[s.album],
        'artist': row[s.artist],
        'lastPlayedTimestamp': row["lastPlayedTimestamp"],
    }