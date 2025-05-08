from .common_fixtures import *
from .common_fixtures import fixture_album_service as fixture_album_service
from musical_chairs_libs.services import AlbumService


def test_get_album(fixture_album_service: AlbumService):
	albumService = fixture_album_service
	data = albumService.get_album(11)
	assert data.name == "boo_album"
	assert len(data.songs) == 5
	