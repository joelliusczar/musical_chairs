from sqlalchemy import create_engine, select, func
from .tables import songs, station_queue, stations
from .history_service import get_history_for_station
from .sql_functions import song_name, album_name, artist_name

def get_queue_for_station(conn, searchBase, stationName):
  q = station_queue.c
  s = songs.c
  st = stations.c
  query = select(s.songPK, s.path, q.addedTimestamp, q.requestedTimestamp, \
    func.song_name(s.path, searchBase).label("songName"),\
    func.album_name(s.path, searchBase).label("albumName"),\
    func.artist_name(s.path, searchBase).label("artistName")) \
    .select_from(station_queue) \
    .join(songs, q.songFK == s.songPK) \
    .join(stations, st.stationPK == q.stationFK) \
    .where(st.name == stationName) \
    .order_by(q.addedTimestamp)
  records = conn.execute(query)
  for row in records:
    yield { 
      'id': row["songPK"],
      'song': row["songName"], 
      'album': row["albumName"],
      'artist': row["artistName"],
      'addedTimestamp': row["addedTimestamp"],
      'requestedTimestamp': row["requestedTimestamp"],
    }

def get_now_playing_and_queue(conn, searchBase, stationName):
    queue = list(get_queue_for_station(conn, searchBase, stationName))
    try:
        playing = next(get_history_for_station(conn, searchBase, stationName, 1))
        return {'nowPlaying':playing, 'items': queue}
    except:
        return {'nowPlaying':'', 'items': queue}

