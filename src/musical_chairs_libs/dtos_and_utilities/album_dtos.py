from .account_dtos import OwnerType
from .artist_dtos import ArtistInfo
from .generic_dtos import (
	FrozenNamed,
	FrozenNamedIdItem,
)
from pydantic import (
	Field,
)
from typing import (
	cast,
	Optional
)
from .station_dtos import StationInfo
from .queued_item import SongListDisplayItem

class AlbumCreationInfo(FrozenNamed):
	year: Optional[int]=None
	albumartist: Optional[ArtistInfo]=None
	versionnote: Optional[str]=""
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)

class AlbumInfo(FrozenNamedIdItem):
	owner: OwnerType
	year: Optional[int]=None
	albumartist: Optional[ArtistInfo]=None
	versionnote: Optional[str]=""

class AlbumListDisplayItem(FrozenNamedIdItem):
	year: Optional[int]=None
	albumartist: Optional[str]=None
	versionnote: Optional[str]=""

class SongsAlbumInfo(AlbumInfo):
	songs: list[SongListDisplayItem]=cast(
		list[SongListDisplayItem], Field(default_factory=list, frozen=False)
	)
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)