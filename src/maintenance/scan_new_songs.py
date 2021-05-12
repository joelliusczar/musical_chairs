import yaml
import os
import re
import sqlite3
from tinytag import TinyTag
from folder_sets import movieSet, gamesSet, popSet, miscSet
from musical_chairs_libs.config_loader import get_config

def getFilter(endings):
  def _filter(str):
    for e in endings:
      if str.endswith(e):
        return True
    return False
  return _filter


config = get_config()

def find_folder_pk(conn, path, folders):
  for folder in folders:
    if folder in path:
      cursor = conn.cursor()
      n = (folder, )
      cursor.execute("SELECT [PK] FROM [Folders] WHERE Name = ?", n)
      pk = cursor.fetchone()[0]
      cursor.close()
      return pk
  raise KeyError("there is no folder for path: %s" % path)

def save_folders(folders ,conn):
  cursor = conn.cursor()
  for folder in folders:
    params = ( folder, )
    try:
      cursor.execute("INSERT INTO [Folders] ([Name]) VALUES(?)", params)
    except: pass

  cursor.close()
  conn.commit()

def scan_files(searchBase):
  searchBaseRgx = r"^" + re.escape(searchBase) + r"/"
  for root, dirs, files in os.walk(searchBase):
    matches = filter(getFilter([".flac", ".mp3",".ogg"]), files)
    if matches:
      subRoot = re.sub(searchBaseRgx, "", root)
      for m in map(lambda m: subRoot + "/" + m, matches):
        yield m

def getTags(songFullPath):
  try:
    tag = TinyTag.get(songFullPath)
    return (tag.title, tag.artist, tag.albumartist, \
       tag.album, tag.track, tag.disc, tag.genre)
  except:
    print(songFullPath)
    fileName = os.path.splitext(os.path.split(songFullPath)[1])[0]
    return (fileName,"","","","","","")

def save_paths(conn, searchBase):
  allFolders = gamesSet | movieSet | popSet | miscSet
  cursor = conn.cursor()
  for path in scan_files(searchBase):
    folderPk = find_folder_pk(conn, path, allFolders)
    params = ( path, folderPk,)
    try:
      cursor.execute("INSERT INTO [Songs] ([Path], [FolderFK]) "
      "VALUES(?, ?)", params)
    except: pass
  cursor.close()
  conn.commit()

def update_metadata(conn, searchBase):
  cursor = conn.cursor()
  page = 0
  pageSize = 5000
  while True:
    offset = page * pageSize
    limit = (page + 1) * pageSize
    cursor.execute("SELECT [PK], [Path] FROM [Songs] "
      "WHERE IFNULL([Title],'') = '' OR "
      "IFNULL([Album],'') = '' OR "
      "IFNULL([Artist],'') = '' "
      "ORDER BY [PK] "
      "LIMIT ?, ?", (offset, limit))
    recordSet = cursor.fetchall()
    for idx, row in enumerate(recordSet):
      print(f"{idx}".rjust(len(str(idx)), " "),end="\r")
      songFullPath = (searchBase + "/" + row[1])
      tagTuple = getTags(songFullPath)
      cursor.execute("UPDATE [Songs] SET "
      "[Title] = ?, "
      "[Artist] = ?, "
      "[AlbumArtist] = ?, "
      "[Album] = ?, "
      "[TrackNum] = ?, "
      "[DiscNum] = ?, "
      "[Genre] = ? "
      "WHERE [PK] = ?", (*tagTuple, row[0]))
    if len(recordSet) < 1:
      break
    page += 1
  cursor.close()
  conn.commit()

def get_tag_pk(conn, tagName):
  cursor = conn.cursor()
  n = (tagName, )
  cursor.execute("SELECT [PK] FROM [Tags] WHERE Name = ?", n)
  pk = cursor.fetchone()[0]
  cursor.close()
  return pk

def get_station_pk(conn, stationName):
  cursor = conn.cursor()
  n = (stationName, )
  cursor.execute("SELECT [PK] FROM [Stations] WHERE Name = ?", n)
  pk = cursor.fetchone()[0]
  cursor.close()
  return pk

def _sort_to_tags(conn, folderName, tagName):
  cursor = conn.cursor()
  tagPk = get_tag_pk(conn, tagName)
  pathParams = ( folderName, )
  for row in cursor.execute("SELECT S.[PK] FROM [Songs] S "
    "JOIN [Folders] F ON S.[FolderFK] = F.[PK] "
    "WHERE F.[Name] = ? ", pathParams):
    params = (row[0], tagPk, )
    writeCursor = conn.cursor()
    try:
      writeCursor.execute("INSERT INTO [SongsTags] ([SongFK], [TagFK]) "
        "VALUES(?, ?)", params)
    except: pass
    finally:
      writeCursor.close()

def sort_to_tags(conn):
  for folder in gamesSet:
    _sort_to_tags(conn, folder, 'vg')
    _sort_to_tags(conn, folder, 'soundtrack')

  for folder in movieSet:
    _sort_to_tags(conn, folder, 'movies')
    _sort_to_tags(conn, folder, 'soundtrack')
  for folder in popSet:
    _sort_to_tags(conn, folder, 'pop')
  conn.commit()

def fresh_start(searchBase, conn):
  print("starting")
  save_folders(gamesSet, conn)
  print("saving game folders done")
  save_folders(movieSet, conn)
  print("saving movie folders done")
  save_folders(popSet, conn)
  print("saving pop folders done")
  save_folders(miscSet, conn)
  print("saving misc folders done")
  save_paths(conn, searchBase)
  print("saving paths done")
  update_metadata(conn, searchBase)
  print("updating songs done")
  sort_to_tags(conn)
  print("all done")

if __name__ == "__main__":
  searchBase = config["searchBase"]
  dbName = config["dbName"]
  conn = sqlite3.connect(dbName)
  fresh_start(searchBase, conn)
  conn.close()