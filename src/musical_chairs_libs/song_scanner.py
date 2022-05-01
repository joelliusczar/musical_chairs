#pyright: reportUnknownMemberType=false
import os
import re
from typing import Callable, \
	Iterator, \
	Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection
from sqlalchemy import insert, \
	select, \
	update
from sqlalchemy.sql import ColumnCollection
from tinytag import TinyTag #pyright: ignore [reportMissingTypeStubs]
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.tables import songs, \
	artists, \
	albums, \
	song_artist, \
	songs_tags
from musical_chairs_libs.station_service import StationService
from collections.abc import Iterable

def getFilter(endings: Iterable[str]) -> Callable[[str],bool]:
	def _filter(str: str) -> bool:
		for e in endings:
			if str.endswith(e):
				return True
		return False
	return _filter

def _append_slash_if_missing(str: str) -> str:
	if not str:
		return str
	return str if str.endswith("/") else f"{str}/"

def scan_files(searchBase: str) -> Iterator[str]:
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

def get_file_tags(songFullPath: str) -> TinyTag:
	fileAndExtIdx = 1
	fileNameNoExtIdx = 0
	try:
		tag: TinyTag = TinyTag.get(songFullPath)
		if not tag.title:
			fileNameNoExt = os.path.splitext(
				os.path.split(songFullPath)[fileAndExtIdx]
			)[fileNameNoExtIdx]
			tag.title = fileNameNoExt #pyright: ignore [reportGeneralTypeIssues]
		return tag
	except:
		print(f"error: {songFullPath}")
		fileName = os.path.splitext(
			os.path.split(songFullPath)[fileAndExtIdx]
		)[fileNameNoExtIdx]

		tag = TinyTag(filehandler=None, filesize=0)
		tag.title = fileName #pyright: ignore [reportGeneralTypeIssues]
		return tag

def map_path_to_tags(path: str) -> Iterable[str]:
	if path.startswith("Soundtrack/VG_Soundtrack"):
		return ["vg", "soundtrack"]
	elif path.startswith("Soundtrack/Movie_Soundtrack"):
		return ["movies", "soundtrack"]
	elif path.startswith("Pop"):
		return ["pop"]
	return []

class SongScanner:

	def __init__(
		self, 
		conn: Connection, 
		stationService: Optional[StationService]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
			if not conn:
				if not envManager:
					envManager = EnvManager()
				conn = envManager.get_configured_db_connection()
			if not stationService:
				stationService = StationService(conn)
			self.conn = conn
			self.station_service = stationService

	def get_or_save_artist(self, name: Optional[str]) -> Optional[int]:
		if not name:
			return None
		a: ColumnCollection = artists.columns
		query = select(a.pk).select_from(artists).where(a.name == name)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(artists).values(name = name)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid 
		return insertedPk

	def get_or_save_album(
		self, 
		name: Optional[str], 
		artistFk: Optional[int]=None, 
		year: Optional[int]=None
	) -> Optional[int]:
		if not name:
			return None
		a: ColumnCollection = albums.columns
		query = select(a.pk).select_from(albums).where(a.name == name)
		row = self.conn.execute(query).fetchone()
		if row:
			pk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
			return pk
		print(name)
		stmt = insert(albums).values(
			name = name, 
			albumArtistFk = artistFk, 
			year = year
		)
		res = self.conn.execute(stmt)
		insertedPk: int = res.lastrowid 
		return insertedPk

	def update_metadata(self, searchBase: str):
		page = 0
		pageSize = 1000
		sg: ColumnCollection = songs.columns
		updateCount = 0
		while True:
			transaction = self.conn.begin()
			offset = page * pageSize
			limit = (page + 1) * pageSize
			query = select(sg.pk, sg.path).select_from(songs) \
				.where(sg.title == None) \
				.limit(limit).offset(offset)
			recordSet = self.conn.execute(query).fetchall()
			for idx, row in enumerate(recordSet):
				print(f"{idx}".rjust(len(str(idx)), " "),end="\r")
				songPath: str = row.path #pyright: ignore [reportGeneralTypeIssues]
				songPk: int = row.pk #pyright: ignore [reportGeneralTypeIssues]
				songFullPath = f"{searchBase}/{songPath}"
				fileTag = get_file_tags(songFullPath)
				artistFk = self.get_or_save_artist(fileTag.artist)
				albumArtistFk = self.get_or_save_artist(fileTag.albumartist)
				albumFk = self.get_or_save_album(
					fileTag.album, 
					albumArtistFk, 
					fileTag.year
				)
				songUpdate = update(songs) \
				.where(sg.pk == songPk) \
				.values(
					title = fileTag.title, 
					albumFk = albumFk, 
					track = fileTag.track, 
					disc = fileTag.disc, 
					bitrate = fileTag.bitrate, 
					comment = fileTag.comment, 
					genre = fileTag.genre
				)
				count: int = self.conn.execute(songUpdate).rowcount 
				updateCount += count
				try:
					songArtistInsert = insert(song_artist)\
						.values(songFk = songPk, artistFk = artistFk)
					self.conn.execute(songArtistInsert)
				except IntegrityError: pass 
			if len(recordSet) < 1:
				break
			page += 1
			transaction.commit()
		return update

	def save_paths(self, searchBase: str) -> int:
		insertCount = 0
		for idx, path in enumerate(scan_files(searchBase)):
			try:
				songInsert = insert(songs).values(path = path)
				songPk: int = self.conn.execute(songInsert).lastrowid 
				insertCount += 1
				self.sort_to_tags(songPk, path)
				print(f"inserted: {idx}".rjust(len(str(idx)), " "),end="\r")
			except IntegrityError: pass
		return insertCount

	def sort_to_tags(self, songPk: int, path: str) -> None:
		for tag in map_path_to_tags(path):
			tagFk = self.station_service.get_tag_pk(tag)
			stmt = insert(songs_tags).values(songFk = songPk, tagFk = tagFk)
			try:
				self.conn.execute(stmt)
			except IntegrityError: pass

