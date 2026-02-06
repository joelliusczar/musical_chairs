from .account_dtos import OwnedEntity
from .generic_dtos import (
	FrozenNamedIdItem,
)

class ArtistInfo(FrozenNamedIdItem, OwnedEntity):
	isprimaryartist: bool=False