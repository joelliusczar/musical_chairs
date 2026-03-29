from musical_chairs_libs.services import (
	JobsService,
)
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	DbConnectionProvider
)
from musical_chairs_libs.services.fs import S3FileService

conn = DbConnectionProvider.get_configured_janitor_connection(
	ConfigAcessors.db_name()
)

fileService = S3FileService()

jobService = JobsService(conn, fileService)

jobService.process_deleted_songs()