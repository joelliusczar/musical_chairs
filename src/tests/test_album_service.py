from .common_fixtures import *
from .common_fixtures import fixture_album_service as fixture_album_service
from musical_chairs_libs.services import AlbumService
from .mocks.db_population import get_initial_songs


def test_get_album(fixture_album_service: AlbumService):
	albumService = fixture_album_service
	data = albumService.get_album(11)
	assert data
	assert data.name == "boo_album"
	assert len(data.songs) == 5
	
def test_get_null_album(fixture_album_service: AlbumService):
	albumService = fixture_album_service
	data = albumService.get_album(None)
	assert data
	noAlbumSongs = [s for s in get_initial_songs() if "albumfk" not in s]
	assert len(data.songs) == len(noAlbumSongs)
