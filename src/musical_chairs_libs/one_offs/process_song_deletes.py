from musical_chairs_libs.services import (
	EnvManager,
	JobsService,
	ArtistService,
	AlbumService,
)
from musical_chairs_libs.services.fs import S3FileService


conn = EnvManager.get_configured_janitor_connection(
	EnvManager.db_name()
)

artistService = ArtistService(conn)
albumService = AlbumService(conn, artistService)

fileService = S3FileService(artistService, albumService)

jobService = JobsService(conn, fileService)

jobService.process_deleted_songs()