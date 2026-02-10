from .account_dtos import OwnedEntity
from .artist_dtos import ArtistInfo, ArtistUnowned
from .generic_dtos import (
	FrozenNamed,
	FrozenNamedIdItem,
	RuledEntity
)
from pydantic import (
	Field,
)
from typing import (
	cast,
	Sequence
)
from .station_dtos import StationInfo, StationUnowned
from .queued_item import SongListDisplayItem


class AlbumCreationInfo(FrozenNamed):
	year: int | None=None
	albumartist: ArtistInfo | ArtistUnowned | None=None
	versionnote: str | None=""
	stations: Sequence[StationInfo | StationUnowned]=cast(
		Sequence[StationInfo | StationUnowned], Field(default_factory=list)
	)

class AlbumUnowned(FrozenNamedIdItem):
	year: int | None=None
	albumartist: ArtistInfo | ArtistUnowned | None=None
	versionnote: str | None=""

class AlbumInfo(AlbumUnowned, RuledEntity, OwnedEntity):
	...


class SongsAlbumInfo(AlbumInfo):
	songs: list[SongListDisplayItem]=cast(
		list[SongListDisplayItem], Field(default_factory=list, frozen=False)
	)
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)