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
  st = stations.c
  sgtg = songs_tags.c
  sttg = stations_tags.c
  tg = tags.c
  query = select(st.pk, st.name, tg.name, tg.pk, \
    func.min(st.displayName)) \
    .select_from(stations) \
    .join(stations_tags, st.pk == sttg.stationFK) \
    .join(songs_tags, sgtg.tagFK == sttg.tagFK) \
    .join(tags, sttg.tagFK == tg.pk) \
    .group_by(st.pk, st.name, tg.name, tg.pk) \
    .having(func.count(sgtg.tagFK) > 0)
  records = conn.execute(query)
  partition = lambda r: (r[st.pk], r[st.name])
  for key, group in itertools.groupby(records, partition):
    yield { 
      "id": key[0],
      "name": key[1], 
      "tags": list(map(lambda r: { 
        "name": r[tg.name],
        "id": r[tg.pk],
      }, group))
    }

def get_station_song_catalogue(
conn, 
stationName, 
limit=50, 
offset=0):
  s = songs.c
  st = stations.c
  sttg = stations_tags.c
  sgtg = songs_tags.c
  query = select(s.pk, s.title, s.album, s.artist) \
    .select_from(stations) \
    .join(stations_tags, st.pk == sttg.stationFK) \
    .join(songs_tags, sgtg.tagFK == sttg.tagFK) \
    .join(songs, s.pk == sgtg.songFK) \
    .where(st.name == stationName) \
    .limit(limit) \
    .offset(offset)
  records = conn.execute(query)
  for row in records:
    yield {
        "id": row[s.pk],
        "song": row[s.title],
        "album": row[s.album],
        "artist": row[s.artist],
    }

def add_song_to_queue(conn, stationName, songPK):
  timestamp = time.time()
  sq = station_queue.c
  st = stations.c
  sttg = stations_tags.c
  sgtg = songs_tags.c

  subquery = select(st.pk) \
    .select_from(stations) \
    .join(stations_tags, sttg.stationFK == st.pk) \
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
        .where(st.pk.in_(subquery)))

  rc = conn.execute(stmt)
  return rc.rowcount