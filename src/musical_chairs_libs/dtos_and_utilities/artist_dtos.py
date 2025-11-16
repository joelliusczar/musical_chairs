from .account_dtos import OwnerType
from .generic_dtos import (
	FrozenNamedIdItem,
)

class ArtistInfo(FrozenNamedIdItem):
	owner: OwnerType
	isprimaryartist: bool=False
