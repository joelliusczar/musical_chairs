import yaml
import os
import re
import sqlite3
from sqlalchemy import insert, create_engine, select
from tinytag import TinyTag
try:
  from musical_chairs_libs.tables import songs, artists, albums, song_artist, songs_tags
  from musical_chairs_libs.config_loader import get_config
  from musical_chairs_libs.queue_manager import get_tag_pk
except ModuleNotFoundError:
  from ..common.tables import songs, artists, albums, song_artist, songs_tags
  from ..common.config_loader import get_config
  from ..common.queue_manager import get_tag_pk

def getFilter(endings):
  def _filter(str):
    for e in endings:
      if str.endswith(e):
        return True
    return False
  return _filter


config = get_config()

def scan_files(searchBase):
  searchBaseRgx = r"^" + re.escape(searchBase) + r"/"
  for root, dirs, files in os.walk(searchBase):
    matches = filter(getFilter([".flac", ".mp3",".ogg"]), files)
    if matches:
      # remove local, non-cloud part of the path
      # i.e. sub with empty str
      subRoot = re.sub(searchBaseRgx, "", root)
      # remember: each file in files is only filename itself
      # not the full path
      # so here, we're gluing the cloud part of the path to
      # the filename name to provide the cloud path
      for m in map(lambda m: subRoot + "/" + m, matches):
        yield m

def get_file_tags(songFullPath):
  try:
    tag = TinyTag.get(songFullPath)
    return tag
  except:
    print(songFullPath)
    fileName = os.path.splitext(os.path.split(songFullPath)[1])[0]
    tag = TinyTag(None, 0)
    tag.title = fileName
    return tag

def get_or_save_artist(conn, name):
  if not name:
    return None
  a = artists.c
  query = select(a.pk).select_from(artists).where(a.name == name)
  row = conn.execute(query).fetchone()
  if row:
    return row.pk
  
  stmt = insert(artists).values(name = name)
  res = conn.execute(stmt)
  return res.lastrowid

def get_or_save_album(conn, name, artistFk = None, year = None):
  if not name:
    return None
  a = albums.c
  query = select(a.pk).select_from(artists).where(a.name == name)
  row = conn.execute(query).fetchone()
  if row:
    return row.pk

  stmt = insert(albums).values(name = name, albumArtistFk = artistFk, year = year)
  res = conn.execute(stmt)
  return res.lastrowid

def save_paths(conn, searchBase):
  transaction = conn.begin()
  for path in scan_files(searchBase):
    params = ( path,)
    songFullPath = f"{searchBase}/{path}"
    fileTag = get_file_tags(songFullPath)
    artistFk = get_or_save_artist(conn, fileTag.artist)
    albumArtistFk = get_or_save_artist(conn, fileTag.albumartist)
    albumFk = get_or_save_album(conn, fileTag.album, albumArtistFk, fileTag.year)
    try:
      songInsert = insert(songs).values(path = path, title = fileTag.title, \
        albumFk = albumFk, track = fileTag.track, disc = fileTag.disc, bitrate = fileTag.bitrate, \
          comment = fileTag.comment, year = fileTag.year, genre = fileTag.genre)
          
      songPk = conn.execute(songInsert).lastrowid
      songArtistInsert = insert(song_artist).values(songFk = songPk, artistFk = artistFk)
      conn.execute(songArtistInsert)
      sort_to_tags(conn, songPk, path)
    except: log_insert_error(f"failed to insert song with path: \n{path}")
  transaction.commit()

def map_path_to_tags(path):
  if path.startswith("Soundtrack/VG_Soundtrack"):
    return ["vg", "soundtrack"]
  elif path.startswith("Soundtrack/Movie_Soundtrack"):
    return ["movies", "soundtrack"]
  elif path.startswith("Pop"):
    return ["pop"]
  return []

def sort_to_tags(conn, songPk, path):
  for tag in map_path_to_tags(path):
    tagFk = get_tag_pk(conn, tag)
    stmt = insert(songs_tags).values(songFk = songPk, tagFk = tagFk)
    try:
      conn.execute(stmt)
    except: log_insert_error(f"Failed to insert association for \npath: {path}\ntag: {tag}")

def log_insert_error(msg):
  printingErrors = False
  if printingErrors:
    print(msg)


def fresh_start(searchBase, conn):
  print("starting")
  save_paths(conn, searchBase)
  print("saving paths done")

if __name__ == "__main__":
  searchBase = config["searchBase"]
  dbName = config["dbName"]
  engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}")
  conn = engine.connect()
  fresh_start(searchBase, conn)