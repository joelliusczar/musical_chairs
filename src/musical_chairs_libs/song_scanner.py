#pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false
import os
import re
from typing import (
	Callable,
	Iterator,
	Optional,
	Iterable
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection
from sqlalchemy import insert
from tinytag import TinyTag
from musical_chairs_libs.dtos_and_utilities import ScanningSongItem
from musical_chairs_libs.services import(
	EnvManager,
	SongInfoService,
	StationService
)

from musical_chairs_libs.tables import songs


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
			for match in (f"{subRoot}/{m}" for m in matches):
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
		conn: Optional[Connection]=None,
		stationService: Optional[StationService]=None,
		envManager: Optional[EnvManager]=None,
		songInfoService: Optional[SongInfoService]=None
	) -> None:
			if not conn:
				if not envManager:
					envManager = EnvManager()
				conn = envManager.get_configured_db_connection()
			if not stationService:
				stationService = StationService(conn)
			if not songInfoService:
				songInfoService = SongInfoService(conn)
			self.conn = conn
			self.station_service = stationService
			self.song_info_service = songInfoService


	def update_metadata(self, searchBase: str) -> int:
		page = 0
		pageSize = 1000
		updateCount = 0
		while True:
			transaction = self.conn.begin()
			songRefs = list(self.song_info_service.get_song_refs(
				songName=None,
				page=page,
				pageSize=pageSize
			))
			print(f"{len(songRefs)} records pulled back")
			for idx, row in enumerate(songRefs):
				print(f"{idx}".rjust(len(str(idx)), " "),end="\r")
				songFullPath = f"{searchBase}/{row.path}"
				fileTag = get_file_tags(songFullPath)
				artistFk = self.song_info_service\
					.get_or_save_artist(fileTag.artist)
				albumArtistFk = self.song_info_service\
					.get_or_save_artist(fileTag.albumartist)
				composerFk = self.song_info_service\
					.get_or_save_artist(fileTag.composer)
				albumFk = self.song_info_service.get_or_save_album(
					fileTag.album,
					albumArtistFk,
					fileTag.year
				)
				songItem = ScanningSongItem(
					id=row.id,
					path=row.path,
					name=fileTag.title,
					albumId=albumFk,
					artistId=artistFk,
					composerId=composerFk,
					track=fileTag.track,
					disc=fileTag.disc,
					genre=fileTag.genre,
					bitrate=fileTag.bitrate,
					samplerate=fileTag.samplerate,
					comment=fileTag.comment,
					duration=fileTag.duration
				)
				updateCount += self.song_info_service.update_song_info(songItem)
			if len(songRefs) < 1:
				break
			page += 1
			transaction.commit()
		return updateCount

	def save_paths(self, searchBase: str) -> int:
		insertCount = 0
		for idx, path in enumerate(scan_files(searchBase)):
			try:
				songInsert = insert(songs).values(path = path)
				self.conn.execute(songInsert).lastrowid
				insertCount += 1
				print(f"inserted: {idx}".rjust(len(str(idx)), " "),end="\r")
			except IntegrityError: pass
		return insertCount


