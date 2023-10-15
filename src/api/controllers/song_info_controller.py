from typing import Optional, Union
from fastapi import (
	APIRouter,
	Depends,
	Security,
	HTTPException,
	status,
	Query,
	UploadFile
)
from fastapi.responses import FileResponse
from api_dependencies import (
	song_info_service,
	get_path_user,
	get_multi_path_user,
	get_user_with_simple_scopes,
	get_path_user_and_check_optional_path,
	get_current_user_simple,
	get_subject_user
)

from musical_chairs_libs.services import SongInfoService
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
	ValidatedSongAboutInfo,
	TableData,
	PathsActionRule
)
from song_validation import (
	extra_validated_song,
	validate_path_rule,
	validate_path_rule_for_remove
)
router = APIRouter(prefix="/song-info")


@router.get("/songs/ls")
def song_ls(
	prefix: Optional[str] = None,
	user: AccountInfo = Security(
		get_path_user,
		scopes=[UserRoleDef.PATH_LIST.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[SongTreeNode]:
	return ListData(items=list(songInfoService.song_ls(user, prefix)))


@router.get("/songs/{itemId}")
def get_song_for_edit(
	itemId: Union[int, str], #optional as str so I can send the correct status code
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_path_user_and_check_optional_path,
		scopes=[UserRoleDef.PATH_VIEW.value]
	)
) -> SongEditInfo:
	if type(itemId) != int:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"{itemId} not found", "id")]
		)
	songInfo = next(songInfoService.get_songs_for_edit([itemId], user), None)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemId} not found", "id")]
	)

#not sure if this will actually be used anywhere. It's mostly a testing
#convenience
@router.get("/songs/list/")
def get_songs_list(
	itemIds: list[int] = Query(default=[]),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_multi_path_user,
		scopes=[UserRoleDef.PATH_VIEW.value]
	)
) -> list[SongEditInfo]:
	return list(songInfoService.get_songs_for_edit(itemIds, user))

@router.get("/songs/multi/")
def get_songs_for_multi_edit(
	itemIds: list[int] = Query(default=[]),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_multi_path_user,
		scopes=[UserRoleDef.PATH_VIEW.value]
	)
) -> SongEditInfo:
	songInfo = songInfoService.get_songs_for_multi_edit(itemIds, user)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"No songs found", "id")]
	)


@router.get(
	"/songs/download/{id}",
	dependencies=[
		Security(
			get_path_user_and_check_optional_path,
			scopes=[UserRoleDef.PATH_DOWNLOAD.value]
		)
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

@router.put("/songs/{itemid}")
def update_song(
	itemid: int,
	song: ValidatedSongAboutInfo = Security(
		extra_validated_song,
		scopes=[UserRoleDef.PATH_EDIT.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_path_user_and_check_optional_path,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> SongEditInfo:
	result = next(songInfoService.save_songs([itemid], song, user=user), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemid} not found", "id")]
	)

@router.put("/songs/multi/")
def update_songs_multi(
	itemIds: list[int] = Query(default=[]),
	song: ValidatedSongAboutInfo = Security(
		extra_validated_song,
		scopes=[UserRoleDef.PATH_EDIT.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_multi_path_user,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> SongEditInfo:
	result = next(songInfoService.save_songs(itemIds, song, user=user), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemIds} not found", "id")]
	)

@router.get("/artists/list")
def get_all_artists(
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[ArtistInfo]:
	return ListData(items=list(songInfoService.get_artists(userId=user.id)))

@router.post("/artists")
def create_artist(
	name: str,
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> ArtistInfo:
	artistInfo = songInfoService.save_artist(user, name)
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
	albumInfo = songInfoService.save_album(album, user=user)
	return albumInfo

@router.get("/albums/list")
def get_all_albums(
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[AlbumInfo]:
	return ListData(items=list(songInfoService.get_albums(userId=user.id)))


@router.get("/path/user_list",dependencies=[
	Security(
		get_path_user_and_check_optional_path,
		scopes=[UserRoleDef.PATH_USER_LIST.value]
	)
])
def get_path_user_list(
	prefix: str,
	songInfoService: SongInfoService = Depends(song_info_service)
) -> TableData[AccountInfo]:
	pathUsers = list(songInfoService.get_path_users(prefix))
	return TableData(pathUsers, len(pathUsers))

@router.post("/path/user_role",
	dependencies=[
		Security(
			get_path_user_and_check_optional_path,
			scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
		)
	]
)
def add_user_rule(
	prefix: str,
	user: AccountInfo = Depends(get_subject_user),
	rule: PathsActionRule = Depends(validate_path_rule),
	songInfoService: SongInfoService = Depends(song_info_service),
) -> PathsActionRule:
	return songInfoService.add_user_rule_to_path(user.id, prefix, rule)

@router.delete("/path/user_role",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			get_path_user_and_check_optional_path,
			scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
		)
	]
)
def remove_user_rule(
	prefix: str,
	user: AccountInfo = Depends(get_subject_user),
	rulename: Optional[str] = Depends(validate_path_rule_for_remove),
	songInfoService: SongInfoService = Depends(song_info_service)
):
	songInfoService.remove_user_rule_from_path(
		user.id,
		prefix,
		rulename
	)

def create_directory(
	prefix: str,
	suffix: str,
	user: AccountInfo = Security(
		get_path_user_and_check_optional_path,
		scopes=[UserRoleDef.PATH_UPLOAD.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service)
):
	pass

def upload_song(
	prefix: str,
	suffix: str,
	file: UploadFile,
	user: AccountInfo = Security(
		get_path_user_and_check_optional_path,
		scopes=[UserRoleDef.PATH_UPLOAD.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service)
):
	pass