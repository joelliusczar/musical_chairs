#pyright: reportMissingTypeStubs=false
import hashlib
from tinytag import TinyTag
from pathlib import Path
from typing import BinaryIO, Tuple
from ..env_manager import EnvManager
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import SongAboutInfo
from ..artist_service import ArtistService
from ..album_service import AlbumService


class LocalFileService(FileService):

	def __init__(
		self,
		artistService: ArtistService,
		albumService: AlbumService
	) -> None:
		self.artist_service = artistService
		self.album_service = albumService

	def __create_missing_directories__(self, keyPath: str):
		savedPath = f"{EnvManager.absolute_content_home()}/{keyPath}"
		path = Path(savedPath)
		path.parents[0].mkdir(parents=True, exist_ok=True)

	def extract_song_info(self, file: BinaryIO) -> SongAboutInfo:
		try:
			songAboutInfo = SongAboutInfo()
			tag = TinyTag.get(file_obj=file) #pyright: ignore [reportUnknownMemberType]
			artist = next(
				self.artist_service.get_artists(
					artistKeys=tag.artist,
					exactStrMatch=True
				),
				None
			)
			album = next(
				self.album_service.get_albums(
					albumKeys=tag.album,
					exactStrMatch=True
				),
				None
			)
			songAboutInfo.primaryartist = artist
			songAboutInfo.album = album
			songAboutInfo.bitrate = float(tag.bitrate) \
				if type(tag.bitrate) == float else None #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
			try:
				songAboutInfo.disc = int(tag.disc or "")
			except:
				pass
			songAboutInfo.genre = tag.genre
			songAboutInfo.duration = tag.duration \
				if type(tag.duration) == float else None #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
			songAboutInfo.name = tag.title
			songAboutInfo.track = tag.track
			return songAboutInfo
		except Exception as e:
			print(e)
			return SongAboutInfo()

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	) -> Tuple[SongAboutInfo, bytes]:
		self.__create_missing_directories__(keyPath)
		savedPath = f"{EnvManager.absolute_content_home()}/{keyPath}"
		with open(savedPath, "wb") as out:
			for chunk in file:
				out.write(chunk)
		with open(savedPath, "rb") as savedFile:
			fileHash = hashlib.sha256(savedFile.read()).digest()
			return self.extract_song_info(savedFile), fileHash


	def open_song(self, keyPath: str) -> BinaryIO:
		return open(keyPath, "rb")

	def download_url(self, keyPath: str) -> str:
		return keyPath

	def delete_song(self, keyPath: str):
		path = Path(keyPath)
		path.unlink()