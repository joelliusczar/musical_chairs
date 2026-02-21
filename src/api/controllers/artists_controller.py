import musical_chairs_libs.dtos_and_utilities as dtos
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
	ArtistInfo,
	RoledUser,
	SongsArtistInfo,
	ListData,
	build_error_obj,
	FrozenNamed,
	SimpleQueryParameters,
	UserRoleSphere,
)
from musical_chairs_libs.services import (
	ArtistService,
)
from api_dependencies import (
	artist_service,
	check_top_level_rate_limit,
	get_secured_artist_by_id,
	get_current_user_simple,
	get_secured_query_params
,)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/artists")



@router.get("/page")
def get_page(
	name: str = "",
	queryParams: SimpleQueryParameters = Security(
		get_secured_query_params,
		scopes=[UserRoleDef.ARTIST_VIEW_ALL.value]
	),
	artistService: ArtistService = Depends(artist_service)
) -> TableData[ArtistInfo]:

	data, totalRows = artistService.get_artist_page(
			artist=name,
			queryParams=queryParams
		)
	return TableData(
		totalrows=totalRows,
		items=data
	)

@router.get("/list")
def get_list(
	artistService: ArtistService = Depends(artist_service),
	user: RoledUser = Security(
		get_current_user_simple,
		scopes=[]
	)
) -> ListData[ArtistInfo]:
	return ListData(items=list(artistService.get_artists(userId=user.id)))


@router.get("/{artistKey}")
def get(
	artistKey: str,
	artistService: ArtistService = Depends(artist_service)
) -> SongsArtistInfo:

	artistInfo = artistService.get_artist(dtos.decode_id(artistKey))
	if not artistInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Artist with key {artistKey} not found")
			]
		)
	return artistInfo


@router.post("", dependencies=[
	Security(
		check_top_level_rate_limit(UserRoleSphere.Artist.value),
		scopes=[UserRoleDef.ARTIST_CREATE.value]
	)
])
def create_artist(
	name: str,
	artistService: ArtistService = Depends(artist_service),
) -> ArtistInfo:
	artistInfo = artistService.save_artist(name)
	if not artistInfo:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=[build_error_obj(f"Artist was not created")
			]
		)
	return artistInfo


@router.put("/{artistid}")
def update_artist(
	artistInfoUpdate: FrozenNamed,
	artist: ArtistInfo = Security(
		get_secured_artist_by_id,
		scopes=[UserRoleDef.ARTIST_EDIT.value]
	),
	artistService: ArtistService = Security(artist_service)
) -> ArtistInfo:
	artistInfo = artistService.save_artist(
		artistName=artistInfoUpdate.name,
		artistId=dtos.decode_id(artist.id)
	)
	if not artistInfo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"Artist with key {artist.id} not found")
			]
		)
	return artistInfo


@router.delete(
	"/{artistid}",
	status_code=status.HTTP_204_NO_CONTENT
)
def delete(
	artist: ArtistInfo = Security(
		get_secured_artist_by_id,
		scopes=[UserRoleDef.ARTIST_EDIT.value]
	),
	artistService: ArtistService = Security(artist_service)
):
	try:
		if artistService.delete_artist(dtos.decode_id(artist.id)) == 0:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj(f"Artist with key {artist.id} not found")
				]
			)
	except IntegrityError:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=[build_error_obj(f"Artist cannot be deleted")
			]
		)