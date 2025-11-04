from musical_chairs_libs.services import (
	JobsService,
	EnvManager,

)
from musical_chairs_libs.services.fs import S3FileService

envManager = EnvManager()
conn = envManager.get_configured_janitor_connection(
	"musical_chairs_db"
)

fileService = S3FileService()

jobService = JobsService(conn, fileService)

jobService.process_deleted_songs()