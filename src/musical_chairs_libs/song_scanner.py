import os
import re
import sys
from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert, create_engine, select, update
from tinytag import TinyTag
from musical_chairs_libs.tables import songs, artists, albums, song_artist, songs_tags
from musical_chairs_libs.config_loader import get_config
from musical_chairs_libs.station_manager import get_tag_pk
from musical_chairs_libs.connection_decorator import provide_db_conn

def getFilter(endings):
	def _filter(str):
		for e in endings:
			if str.endswith(e):
				return True
		return False
	return _filter

def _append_slash_if_missing(str):
	if not str:
		return str
	return str if str.endswith("/") else f"{str}/"

def scan_files(searchBase):
	searchBaseRgx = r"^" + re.escape(_append_slash_if_missing(searchBase))
	for root, _, files in os.walk(searchBase):
		matches = filter(getFilter([".flac", ".mp3",".ogg"]), files)
		if matches:
			# remove local, non-cloud part of the path
			# i.e. sub with empty str
			subRoot = re.sub(searchBaseRgx, "", root)
			# remember: each file in files is only filename itself
			# not the full path
			# so here, we're gluing the cloud part of the path to
			# the filename name to provide the cloud path
			for match in map(lambda m: f"{subRoot}/{m}", matches):
				yield match

def get_file_tags(songFullPath):
	try:
		tag = TinyTag.get(songFullPath)
		if not tag.title:
			fileName = os.path.splitext(os.path.split(songFullPath)[1])[0]
			tag.title = fileName
		return tag
	except:
		print(f"error: {songFullPath}")
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
	print(name)
	stmt = insert(artists).values(name = name)
	res = conn.execute(stmt)
	return res.lastrowid

def get_or_save_album(conn, name, artistFk = None, year = None):
	if not name:
		return None
	a = albums.c
	query = select(a.pk).select_from(albums).where(a.name == name)
	row = conn.execute(query).fetchone()
	if row:
		return row.pk
	print(name)
	stmt = insert(albums).values(name = name, albumArtistFk = artistFk, year = year)
	res = conn.execute(stmt)
	return res.lastrowid

@provide_db_conn()
def update_metadata(searchBase, conn):
	page = 0
	pageSize = 1000
	sg = songs.c
	updateCount = 0
	while True:
		transaction = conn.begin()
		offset = page * pageSize
		limit = (page + 1) * pageSize
		query = select(sg.pk, sg.path).select_from(songs) \
			.where(sg.title == None) \
			.limit(limit).offset(offset)
		recordSet = conn.execute(query).fetchall()
		for idx, row in enumerate(recordSet):
			print(f"{idx}".rjust(len(str(idx)), " "),end="\r")
			songFullPath = f"{searchBase}/{row.path}"
			fileTag = get_file_tags(songFullPath)
			artistFk = get_or_save_artist(conn, fileTag.artist)
			albumArtistFk = get_or_save_artist(conn, fileTag.albumartist)
			albumFk = get_or_save_album(conn, fileTag.album, albumArtistFk, fileTag.year)
			songUpdate = update(songs) \
			.where(sg.pk == row.pk) \
			.values(title = fileTag.title, albumFk = albumFk, track = fileTag.track, \
				disc = fileTag.disc, bitrate = fileTag.bitrate, comment = fileTag.comment, \
				genre = fileTag.genre)
			updateCount += conn.execute(songUpdate).rowcount
			try:
				songArtistInsert = insert(song_artist).values(songFk = row.pk, artistFk = artistFk)
				conn.execute(songArtistInsert)
			except IntegrityError: pass 
		if len(recordSet) < 1:
			break
		page += 1
		transaction.commit()
	return update

@provide_db_conn()
def save_paths(searchBase, conn):
	insertCount = 0
	for idx, path in enumerate(scan_files(searchBase)):
		try:
			songInsert = insert(songs).values(path = path)
			songPk = conn.execute(songInsert).lastrowid
			insertCount += 1
			sort_to_tags(songPk, path, conn)
			print(f"inserted: {idx}".rjust(len(str(idx)), " "),end="\r")
		except IntegrityError: pass
	return insertCount

def map_path_to_tags(path):
	if path.startswith("Soundtrack/VG_Soundtrack"):
		return ["vg", "soundtrack"]
	elif path.startswith("Soundtrack/Movie_Soundtrack"):
		return ["movies", "soundtrack"]
	elif path.startswith("Pop"):
		return ["pop"]
	return []

def sort_to_tags(songPk, path, conn):
	for tag in map_path_to_tags(path):
		tagFk = get_tag_pk(tag, conn)
		stmt = insert(songs_tags).values(songFk = songPk, tagFk = tagFk)
		try:
			conn.execute(stmt)
		except IntegrityError: pass

