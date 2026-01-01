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
	current_user_provider,
	song_info_service,
	song_file_service,
	get_secured_prefix,
	get_current_user_simple,
	get_from_query_subject_user,
	get_prefix_if_owner,
	path_rule_service,
	file_service,
	get_optional_prefix,
	get_prefix,
	get_page_num,
	check_back_key
)
import resource

from musical_chairs_libs.services import (
	CurrentUserProvider,
	SongInfoService,
	SongFileService,
	PathRuleService,
)
from musical_chairs_libs.dtos_and_utilities import (
	SongTreeNode,
	ListData,
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
	get_secured_song_ids,
	validate_path_rule,
	validate_path_rule_for_remove
)
from musical_chairs_libs.protocols import FileService


router = APIRouter(prefix="/song-info")


@router.get("/songs/ls")
def song_ls(
	prefix: Optional[str] = Depends(get_optional_prefix),
	songInfoService: SongFileService = Security(
		song_file_service,
		scopes=[UserRoleDef.PATH_LIST.value]
	),
	currentUserProvider: CurrentUserProvider = Depends(current_user_provider)
) -> ListData[SongTreeNode]:
	items = list(songInfoService.song_ls(prefix))
	if not prefix and len(items) < 1:
		user = currentUserProvider.current_user()
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
	songInfoService: SongFileService = Security(
		song_file_service,
		scopes=[UserRoleDef.PATH_LIST.value]
	)
) -> dict[str, ListData[SongTreeNode]]:
	result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
		) for x
		in songInfoService.song_ls_parents(prefix).items()
	}
	return result


@router.get("/songs/{itemId}")
def get_song_for_edit(
	itemId: int,
	songInfoService: SongInfoService = Security(
		song_info_service,
		scopes=[UserRoleDef.PATH_VIEW.value]
	),
) -> SongEditInfo:
	songInfo = next(songInfoService.get_songs_for_edit([itemId]), None)
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
	itemIds: list[int] = Security(
		get_secured_song_ids,
		scopes=[UserRoleDef.PATH_VIEW.value]
	),
	songInfoService: SongInfoService = Depends(song_info_service),
) -> SongEditInfo:
	songInfo = songInfoService.get_songs_for_multi_edit(itemIds)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"No songs found", "id")]
	)


@router.get(
	"/songs/download/{id}")
def download_song(
	id: list[int] = Security(
		get_secured_song_ids,
		scopes=[UserRoleDef.PATH_DOWNLOAD.value]
	),
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
	songInfoService: SongInfoService = Security(
		song_info_service,
		scopes=[UserRoleDef.PATH_EDIT.value]
	),
) -> SongEditInfo:
	result = next(songInfoService.save_songs([itemid], song), None)
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
	songInfoService: SongInfoService = Security(
		song_info_service,
		scopes=[UserRoleDef.PATH_EDIT.value]
	),
) -> SongEditInfo:
	result = next(songInfoService.save_songs(itemIds, song), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{itemIds} not found", "id")]
	)




@router.get("/path/user_list")
def get_path_user_list(
	prefix: str = Security(
		get_secured_prefix,
		scopes=[UserRoleDef.PATH_USER_LIST.value]
	),
	pathRuleService: PathRuleService = Depends(path_rule_service)
) -> TableData[AccountInfo]:
	pathUsers = list(pathRuleService.get_users_of_path(prefix))
	return TableData(items=pathUsers, totalrows=len(pathUsers))


@router.post("/path/user_role")
def add_user_rule(
	prefix: str = Security(
		get_secured_prefix,
		scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
	),
	subjectuser: AccountInfo = Depends(get_from_query_subject_user),
	rule: PathsActionRule = Depends(validate_path_rule),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> PathsActionRule:
	return pathRuleService.add_user_rule_to_path(subjectuser.id, prefix, rule)


@router.delete("/path/user_role",
	status_code=status.HTTP_204_NO_CONTENT)
def remove_user_rule(
	prefix: str = Security(
		get_secured_prefix,
		scopes=[UserRoleDef.PATH_USER_ASSIGN.value]
	),
	subjectuser: AccountInfo = Depends(get_from_query_subject_user),
	rulename: Optional[str] = Depends(validate_path_rule_for_remove),
	pathRuleService: PathRuleService = Depends(path_rule_service)
):
	pathRuleService.remove_user_rule_from_path(
		subjectuser.id,
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
	songFileService: SongFileService = Security(
		song_file_service,
		scopes=[UserRoleDef.PATH_UPLOAD.value]
	)
) -> dict[str, ListData[SongTreeNode]]:
		result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
			) for x
			in songFileService.create_directory(prefix, suffix).items()
		}
		return result

@router.post("/upload")
def upload_song(
	suffix: str,
	file: UploadFile,
	prefix: str = Depends(get_prefix),
	songFileService: SongFileService = Security(
		song_file_service,
		scopes=[UserRoleDef.PATH_UPLOAD.value]
	)
) -> SongTreeNode:
	return songFileService.save_song_file(file.file, prefix, suffix)


@router.delete("/path/delete_prefix")
def delete_prefix(
	prefix: str = Security(
		get_secured_prefix,
		scopes=[UserRoleDef.PATH_DELETE.value]
	),
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, ListData[SongTreeNode]]:
	result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
		) for x
		in songFileService.delete_prefix(prefix).items()
	}
	return result

@router.post("/path/move")
def move_path(
	transfer: DirectoryTransfer,
	songFileService: SongFileService = Depends(song_file_service)
) -> dict[str, ListData[SongTreeNode]]:
	result = {
		x[0]:ListData(
			items=sorted(x[1], key=SongTreeNode.same_level_sort_key)
		) for x
		in songFileService.move_path(transfer).items()
	}
	return result