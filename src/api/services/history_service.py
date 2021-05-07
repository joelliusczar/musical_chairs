from sqlalchemy import select, desc
from musical_chairs_libs.queue_manager import get_station_pk
from .tables import stations_history, songs
from tinytag import TinyTag


def get_history_for_station(conn, searchBase, stationName, limit = 50):
  station_pk = get_station_pk(conn.connection.connection, stationName)
  if not station_pk:
    return
  h = stations_history.c
  s = songs.c
  query = select(s.songPK, s.path, h.lastPlayedTimestamp) \
    .select_from(stations_history) \
    .join(songs, h.songFK == s.songPK) \
    .where(h.stationFK == station_pk) \
    .order_by(desc(h.lastPlayedTimestamp)) \
    .limit(limit)
  records = conn.execute(query)
  for idx, row in enumerate(records):
    song_full_path = (searchBase + "/" + row["path"]).encode('utf-8')
    try:
        tag = TinyTag.get(song_full_path)
        yield { 
            'id': row["songPK"],
            'song': tag.title, 
            'album': tag.album,
            'artist': tag.artist,
            'lastPlayedTimestamp': row["lastPlayedTimestamp"],
        }
    except:
        yield {
            'id': row["songPK"],
            'lastPlayedTimestamp': row["lastPlayedTimestamp"],
        }