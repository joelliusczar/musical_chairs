from sqlalchemy import select, func, insert, literal, distinct
from .tables import stations, \
  stations_tags, \
  songs_tags, \
  tags, \
  songs, \
  station_queue
from .sql_functions import song_name, album_name, artist_name
import itertools
import time

def get_station_list(conn):
  query = select(stations.c.stationPK, stations.c.name, \
    tags.c.name, tags.c.tagPK) \
    .select_from(stations) \
    .join(stations_tags, stations.c.stationPK == stations_tags.c.stationFK) \
    .join(songs_tags, songs_tags.c.tagFK == stations_tags.c.tagFK) \
    .join(tags, stations_tags.c.tagFK == tags.c.tagPK) \
    .group_by(stations.c.stationPK, stations.c.name, tags.c.name, tags.c.tagPK) \
    .having(func.count(songs_tags.c.tagFK) > 0)
  records = conn.execute(query)
  partition = lambda r: (r[stations.c.stationPK], r[stations.c.name])
  for key, group in itertools.groupby(records, partition):
    yield { 
      "id": key[0],
      "name": key[1], 
      "tags": list(map(lambda r: { 
        "name": r[tags.c.name],
        "id": r[tags.c.tagPK],
      }, group))
    }

def get_station_song_catalogue(
conn, 
searchBase, 
stationName, 
limit=50, 
offset=0):
  s = songs.c
  st = stations.c
  sttg = stations_tags.c
  sgtg = songs_tags.c
  query = select(s.songPK, \
    func.song_name(s.path, searchBase).label("songName"),\
    func.album_name(s.path, searchBase).label("albumName"),\
    func.artist_name(s.path, searchBase).label("artistName")) \
    .select_from(stations) \
    .join(stations_tags, st.stationPK == sttg.stationFK) \
    .join(songs_tags, sgtg.tagFK == sttg.tagFK) \
    .join(songs, s.songPK == sgtg.songFK) \
    .where(st.name == stationName) \
    .limit(limit) \
    .offset(offset)
  records = conn.execute(query)
  for row in records:
    yield {
        "id": row[s.songPK],
        "song": row["songName"],
        "album": row["albumName"],
        "artist": row["artistName"],
    }

def add_song_to_queue(conn, stationName, songPK):
  timestamp = time.time()
  sq = station_queue.c
  st = stations.c
  sttg = stations_tags.c
  sgtg = songs_tags.c

  subquery = select(st.stationPK) \
    .select_from(stations) \
    .join(stations_tags, sttg.stationFK == st.stationPK) \
    .join(songs_tags, sgtg.tagFK == sttg.tagFK) \
    .where(sgtg.songFK == songPK)

  stmt = insert(station_queue).from_select([sq.stationFK, \
    sq.songFK, \
    sq.addedTimestamp, \
    sq.requestedTimestamp], \
    select(
      st.stationPK, \
      literal(songPK), \
      literal(timestamp), \
      literal(timestamp)) \
        .where(st.name == stationName) \
        .where(st.stationPK.in_(subquery)))

  rc = conn.execute(stmt)
  return rc.rowcount