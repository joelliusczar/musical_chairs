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
import musical_chairs_libs.dtos_and_utilities as dtos
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	TableData,
	PlaylistInfo,
	ValidatedPlaylistCreationInfo,
	ActionRule,
	SimpleQueryParameters,
	SongsPlaylistInfo,
	SongPlaylistTuple,
	UserRoleSphere,
)
from musical_chairs_libs.services import (
	PlaylistService,
	PlaylistsUserService,
	PlaylistsSongsService,
	StationsPlaylistsService,
)
from api_dependencies import (
	check_top_level_rate_limit,
	get_owner,
	subject_user,
	build_error_obj,
	playlists_users_service,
	playlist_service,
	playlists_songs_service,
	stations_playlists_service,
	get_query_params,
)
from playlist_validation import (
	get_playlist,
	get_secured_playlist,
	validate_playlist_rule,
	validate_playlist_rule_for_remove
)
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/playlists")	


@router.get("/page")
def get_page(
	name: str="",
	artist: str="",
	owner: dtos.User | None = Depends(get_owner),
	queryParams: SimpleQueryParameters = Depends(get_query_params),
	playService: PlaylistService = Depends(playlist_service)
) -> TableData[PlaylistInfo]:

	data, totalRows = playService.get_playlists_page(
		queryParams,
		owner=owner
	)
	return TableData(
		totalrows=totalRows,
		items=data
	)


@router.get("/list")
def playlist_list(
	owner: dtos.User | None = Depends(get_owner),
	playlistService: PlaylistService = Depends(playlist_service),
) -> Dict[str, List[PlaylistInfo]]:
	playlists = list(playlistService.get_playlists(None,
		ownerId=owner.id if owner else None
	))
	return { "items": playlists }




@router.get("/check/")
def is_phrase_used(
	id: Optional[int]=None,
	name: str = "",
	playlistService: PlaylistService = Depends(playlist_service)
) -> dict[str, bool]:
	return {
		"name": playlistService.is_playlistName_used(id, name)
	}


@router.get("/{ownerkey}/{playlistkey}")
def get_playlist_for_edit(
	playlistInfo: PlaylistInfo = Depends(get_playlist),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	)
) -> SongsPlaylistInfo:
	songs = [*playlistsSongsService.get_songs(playlistInfo.decoded_id())]
	stations = [
		*stationsPlaylistsService.get_stations_by_playlist(
			playlistInfo.decoded_id()
		)
	]
	return SongsPlaylistInfo(
		**playlistInfo.model_dump(),
		songs=songs,
		stations=stations
	)


@router.post("", dependencies=[
	Security(
		check_top_level_rate_limit(UserRoleSphere.Playlist.value),
		scopes=[UserRoleDef.PLAYLIST_CREATE.value]
	)
])
def create_playlist(
	playlist: ValidatedPlaylistCreationInfo = Body(default=None),
	playlistService: PlaylistService = Depends(playlist_service),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	)
) -> SongsPlaylistInfo:
	result = playlistService.save_playlist(playlist)
	songs = [*playlistsSongsService.get_songs(result.decoded_id())]
	stations = [
		*stationsPlaylistsService.get_stations_by_playlist(result.decoded_id())
	]
	return SongsPlaylistInfo(
		**result.model_dump(),
		songs=songs,
		stations=stations
	)


@router.put("/{playlistid}")
def update_playlist(
	savedplaylist: PlaylistInfo = Security(
		get_secured_playlist,
		scopes=[UserRoleDef.PLAYLIST_EDIT.value]
	),
	playlist: ValidatedPlaylistCreationInfo = Body(default=None),
	playlistService: PlaylistService = Depends(playlist_service),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	)
) -> SongsPlaylistInfo:
	result = playlistService.save_playlist(playlist, savedplaylist.decoded_id())
	songs = [*playlistsSongsService.get_songs(savedplaylist.decoded_id())]
	stations = [
		*stationsPlaylistsService.get_stations_by_playlist(
			savedplaylist.decoded_id()
		)
	]
	return SongsPlaylistInfo(
		**result.model_dump(),
		songs=songs,
		stations=stations
	)


@router.get("/{ownerkey}/{playlistkey}/user_list")
def get_playlist_user_list(
	playlistInfo: PlaylistInfo = Security(
		get_secured_playlist,
		scopes=[UserRoleDef.PLAYLIST_USER_LIST.value]
	),
	playlistsUsersService: PlaylistsUserService = Depends(playlists_users_service),
) -> TableData[dtos.RoledUser]:
	playlistUsers = list(playlistsUsersService.get_playlist_users(playlistInfo))
	return TableData(items=playlistUsers, totalrows=len(playlistUsers))


@router.post("/{ownerkey}/{playlistkey}/user_role")
def add_user_rule(
	subjectuser: dtos.User = Depends(subject_user),
	rule: ActionRule = Depends(validate_playlist_rule),
	playlistInfo: PlaylistInfo = Security(
		get_secured_playlist,
		scopes=[UserRoleDef.PLAYLIST_USER_ASSIGN.value]
	),
	playlistsUsersService: PlaylistsUserService = Depends(playlists_users_service),
) -> ActionRule:
	return playlistsUsersService.add_user_rule_to_playlist(
		subjectuser.id,
		playlistInfo.decoded_id(),
		rule
	)


@router.delete("/{ownerkey}/{playlistkey}/user_role",
	status_code=status.HTTP_204_NO_CONTENT)
def remove_user_rule(
	subjectuser: dtos.User = Depends(subject_user),
	rulename: str | None = Depends(validate_playlist_rule_for_remove),
	playlistInfo: PlaylistInfo = Security(
		get_playlist,
		scopes=[UserRoleDef.PLAYLIST_USER_ASSIGN.value]
	),
	playlistsUsersService: PlaylistsUserService = Depends(playlists_users_service),
):
	playlistsUsersService.remove_user_rule_from_playlist(
		subjectuser.id,
		playlistInfo.decoded_id(),
		rulename
	)


@router.delete(
	"/{playlistid}",
	status_code=status.HTTP_204_NO_CONTENT)
def delete(
	playlist: PlaylistInfo = Security(
		get_secured_playlist,
		scopes=[UserRoleDef.PLAYLIST_DELETE.value]
	),
	playlistService: PlaylistService = Depends(playlist_service),
):
	try:
		if playlistService.delete_playlist(playlist.decoded_id()) == 0:
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
	status_code=status.HTTP_204_NO_CONTENT)
def remove_songs(
	playlist: PlaylistInfo = Security(
		get_secured_playlist,
		scopes=[UserRoleDef.PLAYLIST_DELETE.value]
	),
	songids: list[int]=Query(default=[]),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	)
):
	playlistsSongsService.remove_songs_for_playlists((
		SongPlaylistTuple(s, playlist.decoded_id())  for s in songids
	))


@router.post(
	"/{playlistid}/move/{songid}/to/{order}")
def move_songs(
	songid: int,
	order: int,
	playlist: PlaylistInfo = Security(
		get_secured_playlist,
		scopes=[UserRoleDef.PLAYLIST_EDIT.value]
	),
	playlistsSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	)
):
	playlistsSongsService.move_song(playlist.decoded_id(), songid, order)