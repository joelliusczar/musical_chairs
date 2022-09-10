from fastapi import APIRouter, Depends
from api_dependencies import \
	song_info_service
from musical_chairs_libs.services import SongInfoService
from musical_chairs_libs.dtos_and_utilities import SongTreeNode,\
	ListData,\
	AlbumInfo,\
	ArtistInfo

router = APIRouter(prefix="/song-info")

@router.get("/songs/tree")
def song_ls(
	prefix: str = "",
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[SongTreeNode]:
	return ListData(items=list(songInfoService.song_ls(prefix)))


@router.get("/artists/list")
def get_all_artists(
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[ArtistInfo]:
	return ListData(items=list(songInfoService.get_artists()))


@router.get("/albums/list")
def get_all_albums(
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[AlbumInfo]:
	return ListData(items=list(songInfoService.get_albums()))