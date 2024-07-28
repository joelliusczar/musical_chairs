#pyright: reportMissingTypeStubs=false
import boto3
import hashlib
from botocore.client import Config
from typing import BinaryIO, cast, Tuple
from ..env_manager import EnvManager
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import (
	SongAboutInfo,
	guess_contenttype
)
from ..artist_service import ArtistService
from ..album_service import AlbumService
from tinytag import TinyTag
from tempfile import TemporaryFile


class S3FileService(FileService):

	def __init__(
		self,
		artistService: ArtistService,
		albumService: AlbumService
	) -> None:
		self.artist_service = artistService
		self.album_service = albumService

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
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=EnvManager.s3_region_name(),
			)
		)
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			bucket_name=EnvManager.s3_bucket_name(),
			key=keyPath,
		)
		with TemporaryFile() as tmp:
			for chunk in file:
				tmp.write(chunk)
			tmp.seek(0)
			s3_obj.put(Body=tmp, ContentType=guess_contenttype(keyPath)) #pyright: ignore [reportUnknownMemberType]
			tmp.seek(0)
			fileHash = hashlib.sha256(tmp.read()).digest()
			s3_obj.wait_until_exists() #pyright: ignore [reportUnknownMemberType]
			tmp.seek(0)
			return self.extract_song_info(tmp), fileHash



	def open_song(self, keyPath: str) -> BinaryIO:
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=EnvManager.s3_region_name()
			)
		)
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			bucket_name=EnvManager.s3_bucket_name(),
			key=keyPath
		)
		body = s3_obj.get()["Body"] #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
		return cast(BinaryIO, body)

	def download_url(self, keyPath: str) -> str:
		s3Client = boto3.client( #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=EnvManager.s3_region_name()
			)
		)
		url = s3Client.generate_presigned_url( #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
			'get_object',
			Params = {
				'Bucket': EnvManager.s3_bucket_name(),
				'Key': keyPath
			},
			HttpMethod = 'get'
		)
		return cast(str, url)