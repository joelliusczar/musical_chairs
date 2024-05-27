#pyright: reportMissingTypeStubs=false
import boto3
from botocore.client import Config
from typing import BinaryIO, cast
from ..env_manager import EnvManager
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import SongAboutInfo
from ..artist_service import ArtistService
from ..album_service import AlbumService

class S3FileService(FileService):

	def __init__(
		self,
		artistService: ArtistService,
		albumService: AlbumService
	) -> None:
		self.artist_service = artistService
		self.album_service = albumService

	def extract_song_info(self, file: BinaryIO) -> SongAboutInfo:
		return SongAboutInfo()


	def save_song(self, keyPath: str, file: BinaryIO) -> SongAboutInfo:
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=EnvManager.s3_region_name()
			)
		)
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues, reportUnknownVariableType]]
			bucket_name=EnvManager.s3_bucket_name(),
			key=keyPath
		)
		s3_obj.put(Body=file) #pyright: ignore [reportUnknownMemberType]
		s3_obj.wait_until_exists() #pyright: ignore [reportUnknownMemberType]
		return self.extract_song_info(file)



	def open_song(self, keyPath: str) -> BinaryIO:
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=EnvManager.s3_region_name()
			)
		) 
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues, reportUnknownVariableType]]
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