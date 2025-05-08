from typing import Optional
from fastapi import (
	APIRouter,
	Depends,
	Security,
	status
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	TableData,
	AlbumInfo,
	AlbumCreationInfo,
	SongsAlbumInfo,
	ListData
)
from musical_chairs_libs.services import (
	AlbumService,
)
from api_dependencies import (
	get_user_with_simple_scopes,
	album_service,
	get_optional_user_from_token,
	get_page as get_page_num,
	get_current_user_simple
)

router = APIRouter(prefix="/albums")


@router.get("/page")
def get_page(
	limit: int = 50,
	page: int = Depends(get_page_num),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	albumService: AlbumService = Depends(album_service)
) -> TableData[AlbumInfo]:

	data, totalRows = albumService.get_albums_page(
			page = page,
			limit = limit,
			user=user
		)
	return TableData(
		totalrows=totalRows,
		items=data
	)

@router.get("/list")
def get_list(
	albumService: AlbumService = Depends(album_service),
	user: AccountInfo = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[AlbumInfo]:
	return ListData(items=list(albumService.get_albums(userId=user.id)))

@router.get("/{albumkey}")
def get(
	albumkey: int,
	albumService: AlbumService = Depends(album_service)
) -> SongsAlbumInfo:

	albumInfo = albumService.get_album(albumkey)
	return albumInfo


@router.post("")
def create_album(
	album: AlbumCreationInfo,
	albumService: AlbumService = Depends(album_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> AlbumInfo:
	albumInfo = albumService.save_album(album, user=user)
	return albumInfo


@router.put("/{albumkey}")
def update_album(
	albumkey: int,
	album: AlbumCreationInfo,
	albumService: AlbumService = Depends(album_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> AlbumInfo:
	albumInfo = albumService.save_album(album, user=user, albumId=albumkey)
	return albumInfo


@router.delete("{albumkey}", status_code=status.HTTP_204_NO_CONTENT,)
def delete(
	albumkey: int,
	albumService: AlbumService = Depends(album_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
):
	albumService.delete_album(albumkey)


