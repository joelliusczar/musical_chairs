#pyright: reportMissingTypeStubs=false
import boto3
from typing import BinaryIO, cast
from ..env_manager import EnvManager
from .file_service_protocol import FileServiceBase


class S3FileService(FileServiceBase):


	def save_song(self, keyPath: str, file: BinaryIO):
		resource = boto3.resource("s3") #pyright: ignore [reportUnknownMemberType]
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues, reportUnknownVariableType]]
			bucket_name=EnvManager.s3_bucket_name,
			key=keyPath
		)
		s3_obj.put(Body=file) #pyright: ignore [reportUnknownMemberType]
		s3_obj.wait_until_exists() #pyright: ignore [reportUnknownMemberType]



	def open_song(self, keyPath: str) -> BinaryIO:
		resource = boto3.resource("s3") #pyright: ignore [reportUnknownMemberType]
		s3_obj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues, reportUnknownVariableType]]
			bucket_name=EnvManager.s3_bucket_name,
			key=keyPath
		)
		body = s3_obj.get()["Body"] #pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
		return cast(BinaryIO, body)
