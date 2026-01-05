from fastapi import (
	APIRouter,
	Depends,
	Security,
	status,
	HTTPException
)
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	TableData,
	AlbumInfo,
	AlbumCreationInfo,
	SongsAlbumInfo,
	ListData,
	build_error_obj,
	SimpleQueryParameters,
)
from musical_chairs_libs.services import (
	AlbumService,
)
from api_dependencies import (
	album_service,
	check_rate_limit,
	get_query_params,
	get_secured_album_by_id,
)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/albums")	


@router.get("/page")
def get_page(
	name: str="",
	artist: str="",
	queryParams: SimpleQueryParameters = Depends(get_query_params,),
	albumService: AlbumService = Depends(album_service)
) -> TableData[AlbumInfo]:

	data, totalRows = albumService.get_albums_page(
			album=name,
			artist=artist,
			queryParams=queryParams
		)
	return TableData(
		totalrows=totalRows,
		items=data
	)


@router.get("/list")
def get_list(
	albumService: AlbumService = Depends(album_service),
) -> ListData[AlbumInfo]:
	return ListData(items=list(albumService.get_albums()))


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


@router.post("", dependencies=[
	Security(
		check_rate_limit,
		scopes=[UserRoleDef.ALBUM_EDIT.value]
	)
])
def create_album(
	album: AlbumCreationInfo,
	albumService: AlbumService = Depends(album_service),
) -> AlbumInfo:
	albumInfo = albumService.save_album(album)
	if not albumInfo:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=[build_error_obj(f"Album was not created")
			]
		)
	return albumInfo


@router.put("/{albumid}")
def update_album(
	album: AlbumCreationInfo,
	savedalbum: AlbumInfo = Security(
		get_secured_album_by_id,
		scopes=[UserRoleDef.ALBUM_EDIT.value]
	),
	albumService: AlbumService = Depends(album_service)
) -> AlbumInfo:
	albumInfo = albumService.save_album(album, albumId=savedalbum.id)
	if not albumInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Album with key {savedalbum.id} not found")
			]
		)
	return albumInfo


@router.delete(
	"/{albumid}",
	status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
	album: AlbumInfo = Security(
		get_secured_album_by_id,
		scopes=[UserRoleDef.ALBUM_EDIT.value]
	),
	albumService: AlbumService = Depends(album_service),
):
	try:
		if albumService.delete_album(album.id) == 0:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj(f"Album with key {album.id} not found")
				]
			)
	except IntegrityError:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,	
			detail=[build_error_obj(f"Album cannot be deleted")
			]
		)
