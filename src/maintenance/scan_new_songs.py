import yaml
import os
import re
import sqlite3
from folder_sets import movieSet, gamesSet
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
            cursor.execute("SELECT [FolderPK] FROM [Folders] WHERE Name = ?", n)
            pk = cursor.fetchone()[0]
            cursor.close()
            return pk
    return None

def save_folders(folders ,dbName):
    conn = sqlite3.connect(dbName)

    cursor = conn.cursor()

    for folder in folders:
        params = ( folder, )
        try:
            cursor.execute("INSERT INTO [Folders] ([Name]) VALUES(?)",params)
        except: pass

    conn.commit()
    conn.close()

def scan_files(searchBase):
    allFiles = []
    searchBaseRgx = r'^' + re.escape(searchBase) + r'/'
    for root, dirs, files in os.walk(searchBase):
        matches = filter(getFilter(['.flac', '.mp3','.ogg']), files)
        if matches:
            subRoot = re.sub(searchBaseRgx, '', root)
            allFiles.extend(map(lambda m: unicode(subRoot + "/" + m, 'utf-8'), matches))
    return allFiles

def save_paths(allFiles, dbName):
    print(len(allFiles))
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    allFolders = gamesSet | movieSet
    for path in allFiles:
        folderPk = find_folder_pk(conn, path, allFolders)
        params = ( path, folderPk, )
        try:
            cursor.execute("INSERT INTO [Songs] ([Path], [FolderFK]) VALUES(?, ?)",params)
        except: pass

    conn.commit()
    conn.close()

def get_tag_pk(conn, tagName):
    cursor = conn.cursor()
    n = (tagName, )
    cursor.execute("SELECT [TagPK] FROM [Tags] WHERE Name = ?", n)
    pk = cursor.fetchone()[0]
    cursor.close()
    return pk

def get_station_pk(conn, stationName):
    cursor = conn.cursor()
    n = (stationName, )
    cursor.execute("SELECT [StationPK] FROM [Stations] WHERE Name = ?", n)
    pk = cursor.fetchone()[0]
    cursor.close()
    return pk

def _sort_to_tags(conn, folderName, tagName):
    cursor = conn.cursor()
    tagPk = get_tag_pk(conn, tagName)
    pathParams = ( folderName, )
    for row in cursor.execute("SELECT [SongPK] FROM [Songs] S "
        "JOIN [Folders] F ON S.[FolderFK] = F.[FolderPK] "
        "WHERE F.[Name] = ? ", pathParams):
        songTagCursor = conn.cursor()
        params = (row[0], tagPk, )
        songTagCursor.execute("SELECT COUNT(1) FROM [SongsTags] "
            "WHERE [SongFK] = ? and [TagFK] = ? ", params)
        if not songTagCursor.fetchone()[0]:
            writeCursor = conn.cursor()
            writeCursor.execute("INSERT INTO [SongsTags] ([SongFK], [TagFK]) "
                "VALUES(?, ?)", params)
            writeCursor.close()
        songTagCursor.close()

    

def sort_to_tags(dbName):
    conn = sqlite3.connect(dbName)
    for folder in gamesSet:
        _sort_to_tags(conn, folder, 'vg')
        _sort_to_tags(conn, folder, 'soundtrack')

    for folder in movieSet:
        _sort_to_tags(conn, folder, 'movies')
        _sort_to_tags(conn, folder, 'soundtrack')
    conn.commit()
    conn.close()

def insert_station_and_tag(conn, stationName, tagName):
    stationPk = get_station_pk(conn, stationName)
    tagPk = get_tag_pk(conn, tagName)

    cursor = conn.cursor()
    params = (stationPk, tagPk, )
    cursor.execute("INSERT INTO [StationsTags]([StationFK],[TagFK]) VALUES(?, ?)", params)

    cursor.close()

def insert_stations(dbName):
    conn = sqlite3.connect(dbName)
    stationCursor = conn.cursor()
    stationNameParams = [('all', ), ('vg', ), ('thinking', ), ('trip', ), ('pop', ), ('movies', )]
    stationCursor.executemany("INSERT INTO [Stations] ([Name]) VALUES(?)", stationNameParams)
    stationCursor.close()
    allPk = get_station_pk(conn, 'all')

    tagsCursor = conn.cursor()
    tagsCursor.execute("SELECT [TagPK] FROM [Tags]")
    stationTagsParams = map(lambda r: (allPk, r[0], ), tagsCursor.fetchall())
    tagsCursor.close()
    
    tagsStationCursor = conn.cursor()
    tagsStationCursor.executemany("INSERT INTO [StationsTags]([StationFK],[TagFK]) "
        "VALUES(?, ?) ", stationTagsParams)
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
    allFiles = scan_files(searchBase)
    print('scanning paths')
    save_paths(allFiles, dbName)
    print('saving paths done')
    sort_to_tags(dbName)
    print('adding tags done')
    insert_stations(dbName)

if __name__ == '__main__':
    searchBase = config['searchBase']
    dbName = config['dbName']
    #fresh_start(searchBase, dbName)