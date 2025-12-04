from fastapi import (
	APIRouter,
	Depends,
	Security,
	Query
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	PlaylistInfo,
	SongListDisplayItem,
)
from musical_chairs_libs.services import (
	PlaylistsSongsService,
	SongPlaylistTuple
)
from api_dependencies import (
	get_playlist_by_name_and_owner,
	get_optional_user_from_token,
	playlists_songs_service,
	filter_permitter_query_songs,
)
from typing import Dict, List

router = APIRouter(prefix="/playlists/{ownerkey}/{playlistkey}/songs")

@router.get("/list")
def song_list(
	user: AccountInfo = Depends(get_optional_user_from_token),
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
	playlistSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
) -> Dict[str, List[SongListDisplayItem]]:
	songs = list(playlistSongsService.get_songs(
		playlistId=playlistInfo.id,
		user=user
	))
	return { "items": songs }

@router.put("")
def add_songs(
	itemids: list[int] = Query(default=[]),
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
	playlistSongsService: PlaylistsSongsService = Depends(
		playlists_songs_service
	),
	user: AccountInfo = Security(
		filter_permitter_query_songs,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
):
	playlistSongsService.link_songs_with_playlists((
		SongPlaylistTuple(songId, playlistInfo.id) for songId in itemids
	),
	user.id
	)

