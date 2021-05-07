from sqlalchemy import create_engine, select
from .tables import songs, station_queue
from musical_chairs_libs.queue_manager import get_station_pk
from .history_service import get_history_for_station
from tinytag import TinyTag

def get_queue_for_station(conn, searchBase, stationName):
  station_pk = get_station_pk(conn.connection.connection, stationName)
  if not station_pk:
    return
  q = station_queue.c
  s = songs.c
  query = select(s.songPK, s.path, q.addedTimestamp, q.requestedTimestamp) \
    .select_from(station_queue) \
    .join(songs, q.songFK == s.songPK) \
    .where(q.stationFK == station_pk) \
    .order_by(q.addedTimestamp)
  records = conn.execute(query)
  for idx, row in enumerate(records):
    songFullPath = (searchBase + "/" + row[1]).encode('utf-8')
    try:
        tag = TinyTag.get(songFullPath)
        yield { 
            'id': row["songPK"],
            'song': tag.title, 
            'album': tag.album,
            'artist': tag.artist,
            'addedTimestamp': row["addedTimestamp"],
            'requestedTimestamp': row["requestedTimestamp"],
        }
    except:
        yield { 
            'id': row["songPK"],
            'addedTimestamp': row["addedTimestamp"],
            'requestedTimestamp': row["requestedTimestamp"],
        }

def get_now_playing_and_queue(conn, searchBase, stationName):
    queue = list(get_queue_for_station(conn, searchBase, stationName))
    try:
        playing = next(get_history_for_station(conn, searchBase, stationName, 1))
        return {'nowPlaying':playing, 'queue': queue}
    except:
        return {'nowPlaying':'', 'queue': queue}

