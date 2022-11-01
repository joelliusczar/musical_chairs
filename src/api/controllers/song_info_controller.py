from fastapi import\
	APIRouter,\
	Depends,\
	Security,\
	HTTPException,\
	status,\
	Body,\
	Query
from api_dependencies import \
	song_info_service,\
	get_current_user,\
	tag_service
from musical_chairs_libs.services import SongInfoService, TagService
from musical_chairs_libs.dtos_and_utilities import SongTreeNode,\
	ListData,\
	AlbumInfo,\
	ArtistInfo,\
	AccountInfo,\
	UserRoleDef,\
	SongEditInfo,\
	build_error_obj,\
	ValidatedSongAboutInfo
router = APIRouter(prefix="/song-info")

@router.get("/songs/tree")
def song_ls(
	prefix: str = "",
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[SongTreeNode]:
	return ListData(items=list(songInfoService.song_ls(prefix)))


@router.get("/songs/{id}")
def get_song_for_edit(
	id: int,
	songInfoService: SongInfoService = Depends(song_info_service)
) -> SongEditInfo:
	songInfo = next(songInfoService.get_songs_for_edit([id]), None)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{id} not found", "id")]
	)

#not sure if this will actually be used anywhere. It's mostly a testing
#convenience
@router.get("/songs/list/")
def get_songs_list(
	id: list[int] = Query(default=[]),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> list[SongEditInfo]:
	return list(songInfoService.get_songs_for_edit(id))

@router.get("/songs/multi/")
def get_songs_for_multi_edit(
	id: list[int] = Query(default=[]),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> SongEditInfo:
	songInfo = songInfoService.get_songs_for_multi_edit(id)
	if songInfo:
		return songInfo
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"No songs found", "id")]
	)

def extra_validated_song(
	song: ValidatedSongAboutInfo = Body(default=None),
	tagService: TagService = Depends(tag_service),
	songInfoService: SongInfoService = Depends(song_info_service),
) -> ValidatedSongAboutInfo:
	tagIds = {t.id for t in song.tags or []}
	dbTags = {t.id for t in tagService.get_tags(tagIds=tagIds)}
	if tagIds - dbTags:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Tags associated with ids {str(tagIds)} do not exist", "tags")],
		)
	artistIds = {a.id for a in song.allArtists}
	dbArtists = {a.id for a in songInfoService.get_artists(artistIds=artistIds)}
	if artistIds - dbArtists:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Artists associated with ids {str(tagIds)} do not exist", "artists")],
		)
	return song

@router.put("/songs/{id}")
def update_song(
	id: int,
	song: ValidatedSongAboutInfo = Depends(extra_validated_song),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.SONG_EDIT()]
	)
) -> SongEditInfo:
	result = next(songInfoService.save_songs([id], song, userId=user.id), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{id} not found", "id")]
	)

@router.put("/songs/multi/")
def update_songs_multi(
	id: list[int] = Query(default=[]),
	song: ValidatedSongAboutInfo = Depends(extra_validated_song),
	songInfoService: SongInfoService = Depends(song_info_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.SONG_EDIT()]
	)
) -> SongEditInfo:
	result = next(songInfoService.save_songs(id, song, userId=user.id), None)
	if result:
		return result
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"{id} not found", "id")]
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
		get_current_user,
		scopes=[UserRoleDef.ARTIST_EDIT()]
	)
) -> ArtistInfo:
	artistInfo = songInfoService.save_artist(artistName, userId=user.id)
	return artistInfo


@router.get("/albums/list")
def get_all_albums(
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[AlbumInfo]:
	return ListData(items=list(songInfoService.get_albums()))