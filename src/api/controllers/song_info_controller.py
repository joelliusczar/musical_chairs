from typing import Optional, Union
from fastapi import (
	APIRouter,
	Depends,
	Security,
	HTTPException,
	status,
	Query
)
from fastapi.responses import FileResponse
from api_dependencies import (
	song_info_service,
	station_service,
	get_current_user,
	get_path_user,
	get_multi_path_user,
	get_user_with_simple_scopes,
	get_path_user_and_check_optional_path
)
from musical_chairs_libs.services import SongInfoService, StationService
from musical_chairs_libs.dtos_and_utilities import (
	SongTreeNode,
	ListData,
	AlbumInfo,
	AlbumCreationInfo,
	ArtistInfo,
	AccountInfo,
	UserRoleDef,
	SongEditInfo,
	build_error_obj,
	ValidatedSongAboutInfo
)
router = APIRouter(prefix="/song-info")

@router.get("/songs/ls")
def song_ls(
	prefix: Optional[str] = None,
	user: AccountInfo = Security(
		get_path_user_and_check_optional_path,
		scopes=[UserRoleDef.PATH_LIST.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[SongTreeNode]:
	if prefix:
		return ListData(items=list(songInfoService.song_ls(prefix)))
	else:
		prefixes = user.get_permitted_paths(UserRoleDef.PATH_LIST.value)
		return ListData(items=list(songInfoService.song_ls(prefixes)))


@router.get("/songs/{itemId}", dependencies=[
	Security(get_path_user, scopes=[UserRoleDef.PATH_VIEW.value])
])
def get_song_for_edit(
	itemId: Union[int, str],
	songInfoService: SongInfoService = Depends(song_info_service)
) -> SongEditInfo:
	if type(itemId) != int:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"{itemId} not found", "id")]
		)
	songInfo = next(songInfoService.get_songs_for_edit([itemId]), None)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemId} not found", "id")]
	)

#not sure if this will actually be used anywhere. It's mostly a testing
#convenience
@router.get("/songs/list/", dependencies=[
	Security(get_multi_path_user, scopes=[UserRoleDef.PATH_VIEW.value])
])
def get_songs_list(
	itemIds: list[int] = Query(default=[]),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> list[SongEditInfo]:
	return list(songInfoService.get_songs_for_edit(itemIds))

@router.get("/songs/multi/", dependencies=[
	Security(get_multi_path_user, scopes=[UserRoleDef.PATH_VIEW.value])
])
def get_songs_for_multi_edit(
	itemIds: list[int] = Query(default=[]),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> SongEditInfo:
	songInfo = songInfoService.get_songs_for_multi_edit(itemIds)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"No songs found", "id")]
	)

def extra_validated_song(
	song: ValidatedSongAboutInfo,
	stationService: StationService = Depends(station_service),
	songInfoService: SongInfoService = Depends(song_info_service),
) -> ValidatedSongAboutInfo:
	stationIds = {s.id for s in song.stations or []}
	dbStations = {s.id for s in stationService.get_stations(stationIds=stationIds)}
	if stationIds - dbStations:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Stations associated with ids {str(stationIds)} do not exist",
					"Stations"
				)],
		)
	artistIds = {a.id for a in song.allArtists}
	dbArtists = {a.id for a in songInfoService.get_artists(artistIds=artistIds)}
	if artistIds - dbArtists:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Artists associated with ids {str(stationIds)} do not exist", "artists")],
		)
	return song

@router.get(
	"/songs/download/{id}",
	dependencies=[
		Security(get_path_user, scopes=[UserRoleDef.PATH_DOWNLOAD.value])
	],
	response_class=FileResponse
)
def download_song(
	id: int,
	songInfoService: SongInfoService = Depends(song_info_service)
) -> str:
	path = next(songInfoService.get_song_path(id), None)
	if path:
		return path
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{id} not found", "id")]
	)

@router.put("/songs/{itemId}")
def update_song(
	itemId: int,
	song: ValidatedSongAboutInfo = Depends(extra_validated_song),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_path_user,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> SongEditInfo:
	result = next(songInfoService.save_songs([itemId], song, userId=user.id), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemId} not found", "id")]
	)

@router.put("/songs/multi/")
def update_songs_multi(
	itemIds: list[int] = Query(default=[]),
	song: ValidatedSongAboutInfo = Depends(extra_validated_song),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_multi_path_user,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> SongEditInfo:
	result = next(songInfoService.save_songs(itemIds, song, userId=user.id), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemIds} not found", "id")]
	)

@router.get("/artists/list")
def get_all_artists(
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[ArtistInfo]:
	return ListData(items=list(songInfoService.get_artists()))

@router.post("/artists")
def create_artist(
	artistName: str,
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> ArtistInfo:
	artistInfo = songInfoService.save_artist(artistName, userId=user.id)
	return artistInfo

@router.post("/albums")
def create_album(
	album: AlbumCreationInfo,
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> AlbumInfo:
	albumInfo = songInfoService.save_album(album, userId=user.id)
	return albumInfo

@router.get("/albums/list")
def get_all_albums(
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.PATH_VIEW.value]
	)
) -> ListData[AlbumInfo]:
	return ListData(items=list(songInfoService.get_albums()))

