from .common_fixtures import *
from .common_fixtures import (
	fixture_album_service as fixture_album_service,
	fixture_station_service as fixture_station_service
)
from musical_chairs_libs.dtos_and_utilities import (
	AlbumCreationInfo,
)
from musical_chairs_libs.services import AlbumService, StationService
from .mocks.db_population import get_initial_songs


def test_get_album(
	fixture_album_service: AlbumService
):
	albumService = fixture_album_service
	data = albumService.get_album(11)
	assert data
	assert data.name == "boo_album"
	assert len(data.songs) == 5

	data = albumService.get_album(7)
	assert data
	assert data.name == "koo_album"
	assert len(data.stations) == 3
	
def test_get_null_album(fixture_album_service: AlbumService):
	albumService = fixture_album_service
	data = albumService.get_album(None)
	assert data
	noAlbumSongs = [s for s in get_initial_songs() if "albumfk" not in s]
	assert len(data.songs) == len(noAlbumSongs)


@pytest.mark.current_username("testUser_alpha")
def test_save_album_add_stations(
	fixture_album_service: AlbumService,
	fixture_station_service: StationService
):
	albumService = fixture_album_service
	stationService = fixture_station_service

	data = albumService.get_album(7)
	assert data
	data.stations.append(next(iter(stationService.get_stations(27))))
	data.stations.append(next(iter(stationService.get_stations(28))))


	updateDto = AlbumCreationInfo(
		name=data.name,
		year=data.year,
		albumartist=data.albumartist,
		versionnote=data.versionnote,
		stations=data.stations
	)

	albumService.save_album(updateDto, dtos.decode_id(data.id))

	data2 = albumService.get_album(7)
	assert data2

	assert len(data2.stations) == 5

@pytest.mark.current_username("testUser_alpha")
def test_save_album_remove_1_stations(
	fixture_album_service: AlbumService,
):
	albumService = fixture_album_service
	
	data = albumService.get_album(7)
	assert data

	removera = next(
		s for s in data.stations if s.id == dtos.encode_station_id(26)
	)
	data.stations.remove(removera)

	updateDto = AlbumCreationInfo(
		name=data.name,
		year=data.year,
		albumartist=data.albumartist,
		versionnote=data.versionnote,
		stations=data.stations
	)

	albumService.save_album(updateDto, dtos.decode_id(data.id))

	data2 = albumService.get_album(7)
	assert data2

	assert len(data2.stations) == 2
	assert data2.stations[0].id == dtos.encode_station_id(29)

@pytest.mark.current_username("testUser_alpha")
def test_save_album_remove_all_stations(
	fixture_album_service: AlbumService,
):
	albumService = fixture_album_service
	data = albumService.get_album(7)
	assert data

	updateDto = AlbumCreationInfo(
		name=data.name,
		year=data.year,
		albumartist=data.albumartist,
		versionnote=data.versionnote,
		stations=[]
	)

	albumService.save_album(updateDto, dtos.decode_id(data.id))

	data2 = albumService.get_album(7)
	assert data2

	assert len(data2.stations) == 0

@pytest.mark.current_username("testUser_alpha")
def test_save_album_remove_1_add_1_stations(
	fixture_album_service: AlbumService,
	fixture_station_service: StationService
):
	albumService = fixture_album_service
	stationService = fixture_station_service

	data = albumService.get_album(7)
	assert data

	removera = next(
		s for s in data.stations if s.id == dtos.encode_station_id(26)
	)
	data.stations.remove(removera)
	data.stations.append(next(iter(stationService.get_stations(27))))

	updateDto = AlbumCreationInfo(
		name=data.name,
		year=data.year,
		albumartist=data.albumartist,
		versionnote=data.versionnote,
		stations=data.stations
	)

	albumService.save_album(updateDto, dtos.decode_id(data.id))

	data2 = albumService.get_album(7)
	assert data2

	assert len(data2.stations) == 3
	assert data2.stations[0].id == dtos.encode_station_id(27)
	assert data2.stations[1].id == dtos.encode_station_id(29)

@pytest.mark.current_username("testUser_alpha")
def test_save_album_add_first_stations(
	fixture_album_service: AlbumService,
	fixture_station_service: StationService
):
	albumService = fixture_album_service
	stationService = fixture_station_service

	data = albumService.get_album(4)
	assert data
	assert len(data.stations) == 0
	data.stations.append(next(iter(stationService.get_stations(27))))

	# data.stations.append(StationInfo(
	# 	id=28,
	# 	name="album_public_station_bravo"
	# ))

	updateDto = AlbumCreationInfo(
		name=data.name,
		year=data.year,
		albumartist=data.albumartist,
		versionnote=data.versionnote,
		stations=data.stations
	)

	albumService.save_album(updateDto, dtos.decode_id(data.id))

	data2 = albumService.get_album(4)
	assert data2

	assert len(data2.stations) == 1