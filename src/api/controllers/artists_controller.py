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
	ArtistInfo,
	SongsArtistInfo,
	ListData,
	build_error_obj,
	FrozenNamed
)
from musical_chairs_libs.services import (
	ArtistService,
)
from api_dependencies import (
	get_user_with_simple_scopes,
	artist_service,
	user_for_filters,
	get_page_num,
	get_current_user_simple
)
from api_error import (
	build_wrong_permissions_error,
)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/artists")


def can_edit_artist(
	artistid: int,
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.ARTIST_EDIT.value]
	),
	artistService: ArtistService = Depends(artist_service)
) -> AccountInfo:
	if user.isadmin:
		return user
	owner = artistService.get_artist_owner(artistid)
	if owner.id == user.id:
		return user
	raise build_wrong_permissions_error()
	


@router.get("/page")
def get_page(
	name: str = "",
	limit: int = 50,
	page: int = Depends(get_page_num),
	user: Optional[AccountInfo] = Security(
		user_for_filters,
		scopes=[UserRoleDef.ARTIST_VIEW_ALL.value]
	),
	artistService: ArtistService = Depends(artist_service)
) -> TableData[ArtistInfo]:

	data, totalRows = artistService.get_artist_page(
			artist=name,
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
	artistService: ArtistService = Depends(artist_service),
	user: AccountInfo = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[ArtistInfo]:
	return ListData(items=list(artistService.get_artists(userId=user.id)))

@router.get("/{artistKey}")
def get(
	artistKey: int,
	artistService: ArtistService = Depends(artist_service)
) -> SongsArtistInfo:

	artistInfo = artistService.get_artist(artistKey)
	if not artistInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Artist with key {artistKey} not found")
			]
		)
	return artistInfo


@router.post("")
def create_artist(
	name: str,
	artistService: ArtistService = Depends(artist_service),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.PATH_EDIT.value]
	)
) -> ArtistInfo:
	artistInfo = artistService.save_artist(user, name)
	if not artistInfo:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=[build_error_obj(f"Artist was not created")
			]
		)
	return artistInfo


@router.put("/{artistKey}")
def update_artist(
	artistid: int,
	artistInfoUpdate: FrozenNamed,
	artistService: ArtistService = Depends(artist_service),
	user: AccountInfo = Depends(can_edit_artist)
) -> ArtistInfo:
	artistInfo = artistService.save_artist(
		artistName=artistInfoUpdate.name,
		user=user,
		artistId=artistid
	)
	if not artistInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Artist with key {artistid} not found")
			]
		)
	return artistInfo


@router.delete(
	"/{artistid}",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[Depends(can_edit_artist)]
)
def delete(
	artistid: int,
	albumService: ArtistService = Depends(artist_service)
):
	try:
		if albumService.delete_album(artistid) == 0:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj(f"Artist with key {artistid} not found")
				]
			)
	except IntegrityError:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=[build_error_obj(f"Artist cannot be deleted")
			]
		)

