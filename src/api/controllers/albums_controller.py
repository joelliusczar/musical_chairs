from typing import Optional
from fastapi import (
	APIRouter,
	Depends,
	Security,
	status,
	HTTPException
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	TableData,
	AlbumInfo,
	AlbumCreationInfo,
	SongsAlbumInfo,
	ListData,
	build_error_obj
)
from musical_chairs_libs.services import (
	AlbumService,
)
from api_dependencies import (
	album_service,
	get_page_num,
	get_current_user_simple,
	user_for_filters
)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/albums")	


@router.get("/page")
def get_page(
	name: str="",
	artist: str="",
	limit: int = 50,
	page: int = Depends(get_page_num),
	user: Optional[AccountInfo] = Security(
		user_for_filters,
		scopes=[UserRoleDef.ALBUM_VIEW_ALL.value]
	),
	albumService: AlbumService = Depends(album_service)
) -> TableData[AlbumInfo]:

	data, totalRows = albumService.get_albums_page(
			album=name,
			artist=artist,
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


@router.get("/song-counts")
def song_counts_map(
	albumService: AlbumService = Depends(album_service)
) -> dict[int, int]:
	res = albumService.get_song_counts()
	return res


@router.get("/{albumkey}")
def get(
	albumkey: int,
	albumService: AlbumService = Depends(album_service)
) -> SongsAlbumInfo:
	_albumkey = None if albumkey == 0 else albumkey
	albumInfo = albumService.get_album(_albumkey)
	if not albumInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Album with key {albumkey} not found")
			]
		)
	return albumInfo


@router.post("")
def create_album(
	album: AlbumCreationInfo,
	albumService: AlbumService = Security(
		album_service,
		scopes=[UserRoleDef.ALBUM_EDIT.value]
	),
) -> AlbumInfo:
	albumInfo = albumService.save_album(album)
	if not albumInfo:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=[build_error_obj(f"Album was not created")
			]
		)
	return albumInfo


@router.put("/{albumkey}")
def update_album(
	albumkey: int,
	album: AlbumCreationInfo,
	albumService: AlbumService = Security(
		album_service,
		scopes=[UserRoleDef.ALBUM_EDIT.value]
	)
) -> AlbumInfo:
	albumInfo = albumService.save_album(album, albumId=albumkey)
	if not albumInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Album with key {albumkey} not found")
			]
		)
	return albumInfo


@router.delete(
	"/{albumkey}",
	status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
	albumkey: int,
	albumService: AlbumService = Security(
		album_service,
		scopes=[UserRoleDef.ALBUM_EDIT.value]
	),
):
	try:
		if albumService.delete_album(albumkey) == 0:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj(f"Album with key {albumkey} not found")
				]
			)
	except IntegrityError:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,	
			detail=[build_error_obj(f"Album cannot be deleted")
			]
		)
