from .account_dtos import OwnedEntity
from .generic_dtos import (
	FrozenNamedTokenItem,
)


class ArtistUnowned(FrozenNamedTokenItem):
	isprimaryartist: bool=False


class ArtistInfo(ArtistUnowned, OwnedEntity):
	...