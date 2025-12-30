from typing import Iterator, Optional
from fastapi import (
	APIRouter,
	Depends,
	Security,
	HTTPException,
	status,
	Query,
	UploadFile,
)
from fastapi.responses import StreamingResponse
from api_dependencies import (
	song_info_service,
	song_file_service,
	get_path_rule_loaded_current_user,
	get_multi_path_user,
	check_optional_path_for_current_user,
	get_current_user_simple,
	get_from_query_subject_user,
	get_prefix_if_owner,
	path_rule_service,
	file_service,
	album_service,
	artist_service,
	get_optional_prefix,
	get_prefix,
	check_directory_transfer,
	get_page_num,
	check_back_key
)
import resource

from musical_chairs_libs.services import (
	SongInfoService,
	SongFileService,
	PathRuleService,
	AlbumService,
	ArtistService,
)
from musical_chairs_libs.dtos_and_utilities import (
	SongTreeNode,
	ListData,
	AlbumInfo,
	ArtistInfo,
	AccountInfo,
	UserRoleDef,
	SongEditInfo,
	build_error_obj,
	ValidatedSongAboutInfo,
	TableData,
	PathsActionRule,
	SongPathInfo,
	DirectoryTransfer,
	get_path_owner_roles
)
from song_validation import (
	extra_validated_song,
	validate_path_rule,
	validate_path_rule_for_remove
)
from musical_chairs_libs.protocols import FileService


router = APIRouter(prefix="/song-info")


@router.get("/songs/ls")
def song_ls(
	prefix: Optional[str] = Depends(get_optional_prefix),
	user: AccountInfo = Security(
		get_path_rule_loaded_current_user,
		scopes=[UserRoleDef.PATH_LIST.value]
	),
	songInfoService: SongFileService = Depends(song_file_service)
) -> ListData[SongTreeNode]:
	items = list(songInfoService.song_ls(user, prefix))
	if not prefix and len(items) < 1:
		items = [SongTreeNode(
			path=user.dirrootOrDefault,
			totalChildCount= 0,
			directChildren=[],
			rules=list(get_path_owner_roles(user.dirrootOrDefault)),
		)]
	return ListData(items=items)


@router.get("/songs/ls_parents")
def song_ls_parents(
	prefix: str = Depends(get_prefix),
	user: AccountInfo = Security(
		get_path_rule_loaded_current_user,
		scopes=[UserRoleDef.PATH_LIST.value]
	),
	songInfoService: SongFileService = Depends(song_file_service)
) -> dict[str, ListData[SongTreeNode]]:
	result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
		) for x
		in songInfoService.song_ls_parents(user, prefix).items()
	}
	return result


@router.get("/songs/{itemId}")
def get_song_for_edit(
	itemId: int,
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		check_optional_path_for_current_user,
		scopes=[UserRoleDef.PATH_VIEW.value]
	)
) -> SongEditInfo:
	songInfo = next(songInfoService.get_songs_for_edit([itemId], user), None)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemId} not found", "id")]
	)


#not sure if this will actually be used anywhere. It's mostly a testing
#convenience
@router.get("/songs/list/", dependencies=[Depends(check_back_key)])
def get_songs_list(
	limit: Optional[int] = None,
	song: str = "",
	album: str = "",
	albumId: Optional[int]=None,
	artist: str = "",
	artistId: Optional[int]=None,
	page: int = Depends(get_page_num),
	user: AccountInfo = Depends(get_current_user_simple),
	itemIds: Optional[list[int]] = Query(default=None),
	songInfoService: SongInfoService = Depends(song_info_service),
) -> list[SongEditInfo]:
	return list(songInfoService.get_all_songs(
		stationId=None,
		page=page,
		song=song,
		songIds=itemIds,
		album=album,
		albumId=albumId,
		artist=artist,
		artistId=artistId,
		limit=limit,
	))


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
			check_optional_path_for_current_user,
			scopes=[UserRoleDef.PATH_DOWNLOAD.value]
		)
	]
)
def download_song(
	id: int,
	songFileService: SongFileService = Depends(song_file_service),
	fileService: FileService = Depends(file_service)
) -> StreamingResponse:
	mem_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2
	print(f"Used memory: {mem_mib:.2f} MiB")
	path = next(songFileService.get_internal_song_paths(id), None)
	if path:
		def iterfile() -> Iterator[bytes]:
			with fileService.open_song(path) as data:
				if not data:
					raise HTTPException(
						status_code=status.HTTP_404_NOT_FOUND,
						detail=[build_error_obj(f"File not found for {id}", "song file")]
					)
				yield from data

		return StreamingResponse(iterfile())
		
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
		check_optional_path_for_current_user,
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
	artistService: ArtistService = Depends(artist_service),
	user: AccountInfo = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[ArtistInfo]:
	return ListData(items=list(artistService.get_artists(userId=user.id)))


@router.get("/albums/list")
def get_all_albums(
	albumService: AlbumService = Depends(album_service),
	user: AccountInfo = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[AlbumInfo]:
	return ListData(items=list(albumService.get_albums(userId=user.id)))


@router.get("/path/user_list",dependencies=[
	Security(
		check_optional_path_for_current_user,
		scopes=[UserRoleDef.PATH_USER_LIST.value]
	)
])
def get_path_user_list(
	prefix: str = Depends(get_prefix),
	pathRuleService: PathRuleService = Depends(path_rule_service)
) -> TableData[AccountInfo]:
	pathUsers = list(pathRuleService.get_users_of_path(prefix))
	return TableData(items=pathUsers, totalrows=len(pathUsers))


@router.post("/path/user_role",
	dependencies=[
		Security(
			check_optional_path_for_current_user,
			scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
		)
	]
)
def add_user_rule(
	prefix: str = Depends(get_prefix),
	user: AccountInfo = Depends(get_from_query_subject_user),
	rule: PathsActionRule = Depends(validate_path_rule),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> PathsActionRule:
	return pathRuleService.add_user_rule_to_path(user.id, prefix, rule)


@router.delete("/path/user_role",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			check_optional_path_for_current_user,
			scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
		)
	]
)
def remove_user_rule(
	prefix: str = Depends(get_prefix),
	user: AccountInfo = Depends(get_from_query_subject_user),
	rulename: Optional[str] = Depends(validate_path_rule_for_remove),
	pathRuleService: PathRuleService = Depends(path_rule_service)
):
	pathRuleService.remove_user_rule_from_path(
		user.id,
		prefix,
		rulename
	)


@router.get("/check/",
	dependencies=[
		Depends(get_current_user_simple)
	]
)
def is_phrase_used(
	id: Optional[int]=None,
	suffix: str = "",
	prefix: str = Depends(get_prefix_if_owner),
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, bool]:
	return {
		"suffix": songFileService.is_path_used(id, prefix, suffix)
	}

@router.put("/check_multi/",
	dependencies=[
		Depends(get_current_user_simple)
	]
)
def are_paths_used(
	songSuffixes: list[SongPathInfo],
	prefix: str = Depends(get_prefix_if_owner),
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, bool]:
	return songFileService.are_paths_used(prefix, songSuffixes)


@router.post("/directory")
def create_directory(
	suffix: str,
	prefix: str = Depends(get_prefix),
	user: AccountInfo = Security(
		check_optional_path_for_current_user,
		scopes=[UserRoleDef.PATH_UPLOAD.value]
	),
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, ListData[SongTreeNode]]:
		result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
			) for x
			in songFileService.create_directory(prefix, suffix, user).items()
		}
		return result

@router.post("/upload")
def upload_song(
	suffix: str,
	file: UploadFile,
	prefix: str = Depends(get_prefix),
	user: AccountInfo = Security(
		check_optional_path_for_current_user,
		scopes=[UserRoleDef.PATH_UPLOAD.value]
	),
	songFileService: SongFileService = Depends(song_file_service)
) -> SongTreeNode:
	return songFileService.save_song_file(file.file, prefix, suffix, user.id)


@router.delete("/path/delete_prefix")
def delete_prefix(
	prefix: str = Depends(get_prefix),
	user: AccountInfo = Security(
		check_optional_path_for_current_user,
		scopes=[UserRoleDef.PATH_DELETE.value]
	),
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, ListData[SongTreeNode]]:
	result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
		) for x
		in songFileService.delete_prefix(prefix, user).items()
	}
	return result

@router.post("/path/move")
def move_path(
	transfer: DirectoryTransfer,
	user: AccountInfo = Security(
		check_directory_transfer,
		scopes=[UserRoleDef.PATH_MOVE.value]
	),
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, ListData[SongTreeNode]]:
	result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
		) for x
		in songFileService.move_path(transfer, user).items()
	}
	return result