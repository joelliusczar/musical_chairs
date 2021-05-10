from sqlalchemy import create_engine, select, func
from .tables import songs, station_queue, stations
from .history_service import get_history_for_station
from .sql_functions import song_name, album_name, artist_name

def get_queue_for_station(conn, stationName):
  q = station_queue.c
  s = songs.c
  st = stations.c
  query = select(s.pk, q.addedTimestamp, q.requestedTimestamp, \
    s.title, s.album, s.artist) \
    .select_from(station_queue) \
    .join(songs, q.songFK == s.pk) \
    .join(stations, st.pk == q.stationFK) \
    .where(st.name == stationName) \
    .order_by(q.addedTimestamp)
  records = conn.execute(query)
  for row in records:
    yield { 
      'id': row[s.pk],
      'song': row[s.title], 
      'album': row[s.album],
      'artist': row[s.artist],
      'addedTimestamp': row["addedTimestamp"],
      'requestedTimestamp': row["requestedTimestamp"],
    }

def get_now_playing_and_queue(conn, stationName):
    queue = list(get_queue_for_station(conn, stationName))
    try:
        playing = next(get_history_for_station(conn, stationName, 1))
        return {'nowPlaying':playing, 'items': queue}
    except:
        return {'nowPlaying':'', 'items': queue}

