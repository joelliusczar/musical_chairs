from .common_fixtures import (
	fixture_account_service as fixture_account_service,
	fixture_stations_albums_service as fixture_stations_albums_service
)
from musical_chairs_libs.services import (
	AccountsService,
	StationsAlbumsService
)
from .common_fixtures import *

def test_get_stations_by_album(
	fixture_stations_albums_service: StationsAlbumsService,
	fixture_account_service: AccountsService
):
	stationAlbumService = fixture_stations_albums_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user

	data = sorted(
		stationAlbumService.get_stations_by_album(9, user),
		key=lambda s:s.id
	)

	assert len(data) == 3
	assert data[0].name == "album_public_station_alpha"
	assert data[1].name == "album_public_station_bravo"

	data = sorted(
		stationAlbumService.get_stations_by_album(10, user),
		key=lambda s:s.id
	)

	assert len(data) == 1
	assert data[0].name == "album_public_station_alpha"

	data = sorted(
		stationAlbumService.get_stations_by_album(7, user),
		key=lambda s:s.id
	)

	assert len(data) == 3
	assert data[0].name == "album_public_station_alpha"
	assert data[1].name == "album_public_station_charlie"
