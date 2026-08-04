import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.protocols as protocols
from .local_file_service import LocalFileService
from .s3_file_service import S3FileService

LOCAL_FILES = "LOCAL"

class FileServiceFactory:

	@classmethod
	def get_file_service(cls) -> protocols.FileService:
		if dtos.ConfigAcessors.file_env() == LOCAL_FILES:
			return LocalFileService()
		else:
			return S3FileService()