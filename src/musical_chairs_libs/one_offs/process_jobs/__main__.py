from musical_chairs_libs.services import (
	JobsService,
	EnvManager,

)
from musical_chairs_libs.services.fs import S3FileService

conn = EnvManager.get_configured_janitor_connection(
	EnvManager.db_name()
)

fileService = S3FileService()

jobService = JobsService(conn, fileService)

jobService.process_deleted_songs()