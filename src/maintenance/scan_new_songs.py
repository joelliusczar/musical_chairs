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

def save_folders(folders ,dbName):
  conn = sqlite3.connect(dbName)

  for folder in folders:
    params = ( folder, )
    cursor = conn.cursor()
    try:
      cursor.execute("INSERT INTO [Folders] ([Name]) VALUES(?)",params)
    except: pass
    finally:
      cursor.close()

  conn.commit()
  conn.close()

def scan_files(searchBase):
  allFiles = []
  searchBaseRgx = r'^' + re.escape(searchBase) + r'/'
  for root, dirs, files in os.walk(searchBase):
    matches = filter(getFilter(['.flac', '.mp3','.ogg']), files)
    if matches:
      subRoot = re.sub(searchBaseRgx, '', root)
      allFiles.extend(map(lambda m: subRoot + "/" + m, matches))
  return allFiles

def getTags(songFullPath):
  try:
    tag = TinyTag.get(songFullPath)
    return (tag.title, tag.artist, tag.albumartist, \
       tag.album, tag.track, tag.disc, tag.genre)
  except:
    print(songFullPath)
    fileName = os.path.splitext(os.path.split(songFullPath)[1])
    return (fileName,"","","","","","","",)

def save_paths(allFiles, dbName, searchBase):
  print(len(allFiles))
  conn = sqlite3.connect(dbName)
  
  allFolders = gamesSet | movieSet | popSet | miscSet
  
  for idx, path in enumerate(allFiles):
    print(f"{idx}".rjust(len(allFiles), " "),end="\r")
    folderPk = find_folder_pk(conn, path, allFolders)
    songFullPath = (searchBase + "/" + path)
    tagTuple = getTags(songFullPath)
    params = ( path, folderPk, *tagTuple)
    cursor = conn.cursor()
    try:
      cursor.execute("INSERT INTO [Songs] ([Path], [FolderFK], "
      "[Title], [Artist], [AlbumArtist], [Album], [TrackNum], "
      "[DiscNum], [Genre]) "
      "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
    except: pass
    finally:
      cursor.close()

  conn.commit()
  conn.close()

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
  for row in cursor.execute("SELECT [PK] FROM [Songs] S "
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


  

def sort_to_tags(dbName):
  conn = sqlite3.connect(dbName)
  for folder in gamesSet:
    _sort_to_tags(conn, folder, 'vg')
    _sort_to_tags(conn, folder, 'soundtrack')

  for folder in movieSet:
    _sort_to_tags(conn, folder, 'movies')
    _sort_to_tags(conn, folder, 'soundtrack')
  for folder in popSet:
    _sort_to_tags(conn, folder, 'pop')
  conn.commit()
  conn.close()

def insert_station_and_tag(conn, stationName, tagName):
  stationPk = get_station_pk(conn, stationName)
  tagPk = get_tag_pk(conn, tagName)

  cursor = conn.cursor()
  params = (stationPk, tagPk, )
  try:
    cursor.execute("INSERT INTO [StationsTags]([StationFK],[TagFK]) VALUES(?, ?)", params)
  except: pass
  finally:
    cursor.close()

def insert_stations(dbName):
  conn = sqlite3.connect(dbName)
  stationCursor = conn.cursor()
  try:
    stationNameParams = [('all', ), ('vg', ), ('thinking', ), ('trip', ), ('pop', ), ('movies', )]
    stationCursor.executemany("INSERT INTO [Stations] ([Name]) VALUES(?)", stationNameParams)
  except: pass
  finally:
    stationCursor.close()
  allPk = get_station_pk(conn, 'all')

  tagsCursor = conn.cursor()
  tagsCursor.execute("SELECT [PK] FROM [Tags]")
  stationTagsParams = map(lambda r: (allPk, r[0], ), tagsCursor.fetchall())
  tagsCursor.close()
  
  tagsStationCursor = conn.cursor()
  try:
    tagsStationCursor.executemany("INSERT INTO [StationsTags]([StationFK],[TagFK]) "
      "VALUES(?, ?) ", stationTagsParams)
  except: pass
  finally:
    tagsStationCursor.close()

  insert_station_and_tag(conn, 'vg', 'vg')
  insert_station_and_tag(conn, 'thinking', 'thinking')
  insert_station_and_tag(conn, 'pop', 'pop')
  insert_station_and_tag(conn, 'trip', 'trippy')

  conn.commit()
  conn.close()

def fresh_start(searchBase, dbName):
  print('starting')
  save_folders(gamesSet, dbName)
  print('saving game folders done')
  save_folders(movieSet, dbName)
  print('saving movie folders done')
  save_folders(popSet, dbName)
  print('saving pop folders done')
  save_folders(miscSet, dbName)
  print('saving misc folders done')
  allFiles = scan_files(searchBase)
  print('scanning paths')
  save_paths(allFiles, dbName, searchBase)
  print('saving paths done')
  sort_to_tags(dbName)
  print('adding tags done')
  insert_stations(dbName)

if __name__ == '__main__':
  searchBase = config['searchBase']
  dbName = config['dbName']
  fresh_start(searchBase, dbName)