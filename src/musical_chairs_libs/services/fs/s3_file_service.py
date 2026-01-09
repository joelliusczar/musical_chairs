#pyright: reportMissingTypeStubs=false
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from typing import BinaryIO, cast, IO
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors
)
from tempfile import NamedTemporaryFile


class S3FileService(FileService):

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	) -> IO[bytes]:

		tmp = NamedTemporaryFile()
		for chunk in file:
			tmp.write(chunk)	
		tmp.seek(0)

		s3_client = boto3.client( #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
			"s3",
			region_name=ConfigAcessors.s3_region_name()
		)
		config = TransferConfig()
	
		s3_client.upload_file( #pyright: ignore [reportUnknownMemberType]
			Filename=tmp.name,
			Bucket=ConfigAcessors.s3_bucket_name(),
			Key=keyPath,
			Config=config
		)

		tmp.seek(0)
		return tmp



	def open_song(self, keyPath: str) -> BinaryIO:
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=ConfigAcessors.s3_region_name()
			)
		)
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			bucket_name=ConfigAcessors.s3_bucket_name(),
			key=keyPath
		)
		body = s3_obj.get()["Body"] #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
		return cast(BinaryIO, body)


	def download_url(self, keyPath: str) -> str:
		s3Client = boto3.client( #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=ConfigAcessors.s3_region_name()
			)
		)
		url = s3Client.generate_presigned_url( #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
			'get_object',
			Params = {
				'Bucket': ConfigAcessors.s3_bucket_name(),
				'Key': keyPath
			},
			HttpMethod = 'get'
		)
		return cast(str, url)


	def delete_song(self, keyPath: str):
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=ConfigAcessors.s3_region_name()
			)
		)
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			bucket_name=ConfigAcessors.s3_bucket_name(),
			key=keyPath
		)
		s3_obj.delete() #pyright: ignore [reportUnknownMemberType]

	def song_absolute_path(self, keyPath: str) -> str:
		return keyPath