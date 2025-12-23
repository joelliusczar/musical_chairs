#pyright: reportMissingTypeStubs=false
from typing import Dict, List, Optional
from fastapi import (
	APIRouter,
	Depends,
	Security,
	HTTPException,
	status,
	Body,
	Query,
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	TableData,
	PlaylistInfo,
	ValidatedPlaylistCreationInfo,
	PlaylistActionRule,
	SongsPlaylistInfo,
	SongPlaylistTuple,
)
from musical_chairs_libs.services import (
	PlaylistService,
	PlaylistsUserService,
	PlaylistsSongsService,
	StationsPlaylistsService,
)
from api_dependencies import (
	get_owner_from_query,
	get_playlist_by_name_and_owner,
	get_user_with_rate_limited_scope,
	get_optional_user_from_token,
	get_from_query_subject_user,
	build_error_obj,
	get_playlist_user_by_id,
	playlists_users_service,
	playlist_service,
	get_playlist_user,
	get_page_num,
	user_for_filters,
	get_current_user_simple,
	playlists_songs_service,
	stations_playlists_service,
)
from playlist_validation import (
	validate_playlist_rule,
	validate_playlist_rule_for_remove
)
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/playlists")	


@router.get("/page")
def get_page(
	name: str="",
	artist: str="",
	limit: int = 50,
	page: int = Depends(get_page_num),
	user: Optional[AccountInfo] = Security(
		user_for_filters,
		scopes=[UserRoleDef.PLAYLIST_VIEW.value]
	),
	playService: PlaylistService = Depends(playlist_service)
) -> TableData[PlaylistInfo]:

	data, totalRows = playService.get_playlists_page(
			page = page,
			limit = limit,
			user=user
		)
	return TableData(
		totalrows=totalRows,
		items=data
	)


@router.get("/list")
def playlist_list(
	user: AccountInfo = Depends(get_optional_user_from_token),
	owner: Optional[AccountInfo] = Depends(get_owner_from_query),
	playlistService: PlaylistService = Depends(playlist_service),
) -> Dict[str, List[PlaylistInfo]]:
	playlists = list(playlistService.get_playlists(None,
		ownerId=owner.id if owner else None,
		user=user
	))
	return { "items": playlists }




@router.get("/check/")
def is_phrase_used(
	id: Optional[int]=None,
	name: str = "",
	user: AccountInfo = Depends(get_current_user_simple),
	playlistService: PlaylistService = Depends(playlist_service)
) -> dict[str, bool]:
	return {
		"name": playlistService.is_playlistName_used(id, name, user.id)
	}


@router.get("/{ownerkey}/{playlistkey}")
def get_playlist_for_edit(
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	)
) -> SongsPlaylistInfo:
	songs = [*playlistsSongsService.get_songs(playlistInfo.id)]
	stations = [
		*stationsPlaylistsService.get_stations_by_playlist(playlistInfo.id)
	]
	return SongsPlaylistInfo(
		**playlistInfo.model_dump(),
		songs=songs,
		stations=stations
	)


@router.post("")
def create_playlist(
	playlist: ValidatedPlaylistCreationInfo = Body(default=None),
	playlistService: PlaylistService = Depends(playlist_service),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	),
	user: AccountInfo = Security(
		get_user_with_rate_limited_scope,
		scopes=[UserRoleDef.PLAYLIST_CREATE.value]
	)
) -> SongsPlaylistInfo:
	result = playlistService.save_playlist(playlist, user=user)
	songs = [*playlistsSongsService.get_songs(result.id)]
	stations = [
		*stationsPlaylistsService.get_stations_by_playlist(result.id)
	]
	return SongsPlaylistInfo(
		**result.model_dump(),
		songs=songs,
		stations=stations
	)


@router.put("/{playlistid}")
def update_playlist(
	playlistid: int, #this needs to match get_playlist_user_by_id
	playlist: ValidatedPlaylistCreationInfo = Body(default=None),
	playlistService: PlaylistService = Depends(playlist_service),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	),
	user: AccountInfo = Security(
		get_playlist_user_by_id,
		scopes=[UserRoleDef.PLAYLIST_EDIT.value]
	)
) -> SongsPlaylistInfo:
	result = playlistService.save_playlist(playlist, user, playlistid)
	songs = [*playlistsSongsService.get_songs(result.id)]
	stations = [
		*stationsPlaylistsService.get_stations_by_playlist(result.id)
	]
	return SongsPlaylistInfo(
		**result.model_dump(),
		songs=songs,
		stations=stations
	)



@router.get("/{ownerkey}/{playlistkey}/user_list",dependencies=[
	Security(
		get_playlist_user,
		scopes=[UserRoleDef.PLAYLIST_USER_LIST.value]
	)
])
def get_playlist_user_list(
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
	playlistsUsersService: PlaylistsUserService = Depends(playlists_users_service),
) -> TableData[AccountInfo]:
	playlistUsers = list(playlistsUsersService.get_playlist_users(playlistInfo))
	return TableData(items=playlistUsers, totalrows=len(playlistUsers))


@router.post("/{ownerkey}/{playlistkey}/user_role",
	dependencies=[
		Security(
			get_playlist_user,
			scopes=[UserRoleDef.PLAYLIST_USER_ASSIGN.value]
		)
	]
)
def add_user_rule(
	user: AccountInfo = Depends(get_from_query_subject_user),
	rule: PlaylistActionRule = Depends(validate_playlist_rule),
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
	playlistsUsersService: PlaylistsUserService = Depends(playlists_users_service),
) -> PlaylistActionRule:
	return playlistsUsersService.add_user_rule_to_playlist(
		user.id,
		playlistInfo.id,
		rule
	)


@router.delete("/{ownerkey}/{playlistkey}/user_role",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			get_playlist_user,
			scopes=[UserRoleDef.PLAYLIST_USER_ASSIGN.value]
		)
	]
)
def remove_user_rule(
	user: AccountInfo = Depends(get_from_query_subject_user),
	rulename: Optional[str] = Depends(validate_playlist_rule_for_remove),
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
	playlistsUsersService: PlaylistsUserService = Depends(playlists_users_service),
):
	playlistsUsersService.remove_user_rule_from_playlist(
		user.id,
		playlistInfo.id,
		rulename
	)

@router.delete(
	"/{playlistid}",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[Security(
		get_playlist_user_by_id,
		scopes=[UserRoleDef.PLAYLIST_DELETE.value]
	)]
)
def delete(
	playlistid: int,
	playlistService: PlaylistService = Depends(playlist_service),
):
	try:
		if playlistService.delete_playlist(playlistid) == 0:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj(f"Playlist not found")
				]
			)
	except IntegrityError:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,	
			detail=[build_error_obj(f"Playlist cannot be deleted")
			]
		)
	

@router.delete("/{playlistid}/songs",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			get_playlist_user_by_id,
			scopes=[UserRoleDef.PLAYLIST_EDIT.value]
		)
	]
)
def remove_songs(
	playlistid: int,
	songids: list[int]=Query(default=[]),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	)
):
	playlistsSongsService.remove_songs_for_playlists((
		SongPlaylistTuple(s, playlistid)  for s in songids
	))

@router.post(
	"/{playlistid}/move/{songid}/to/{order}",
	dependencies=[
		Security(
			get_playlist_user_by_id,
			scopes=[UserRoleDef.PLAYLIST_EDIT.value]
		)
	]
)
def move_songs(
	playlistid: int,
	songid: int,
	order: int,
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	)
):
	playlistsSongsService.move_song(playlistid, songid, order)