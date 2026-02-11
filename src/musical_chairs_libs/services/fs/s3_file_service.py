#pyright: reportMissingTypeStubs=false
import boto3
from botocore.client import Config
from typing import BinaryIO, cast
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import (
	guess_contenttype,
	ConfigAcessors
)



class S3FileService(FileService):

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	):
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
			"s3",
			config=Config(
				signature_version='s3v4',
				region_name=ConfigAcessors.s3_region_name(),
			)
		)
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			bucket_name=ConfigAcessors.s3_bucket_name(),
			key=keyPath,
		)
		
		s3_obj.put(Body=file, ContentType=guess_contenttype(keyPath)) #pyright: ignore [reportUnknownMemberType]

		s3_obj.wait_until_exists() #pyright: ignore [reportUnknownMemberType]
		file.seek(0)



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
		versionId = s3_obj.version_id #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
		s3_obj.delete(VersionId=versionId) #pyright: ignore [reportUnknownMemberType]

	def song_absolute_path(self, keyPath: str) -> str:
		return keyPath