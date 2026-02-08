from .account_dtos import OwnedEntity
from .generic_dtos import (
	FrozenNamedIdItem,
)


class ArtistUnowned(FrozenNamedIdItem):
	isprimaryartist: bool=False


class ArtistInfo(ArtistUnowned, OwnedEntity):
	...