from fastapi import APIRouter, Depends
from api_dependencies import \
	song_info_service
from musical_chairs_libs.song_info_service import SongInfoService
from musical_chairs_libs.dtos_and_utilities import SongTreeNode, ListData

router = APIRouter(prefix="/song-info")

@router.get("/tree")
def song_ls(
	prefix: str = "",
	songInfoService: SongInfoService = Depends(song_info_service)
) -> ListData[SongTreeNode]:
	return ListData(items=list(songInfoService.song_ls(prefix)))
