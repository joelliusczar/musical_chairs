from .account_dtos import AccountInfo
from .generic_dtos import (
	MCBaseClass,
)
from typing import Iterable, Optional

class SimpleQueryParameters(MCBaseClass):
	page: int = 0
	limit: Optional[int]=None
	user: Optional[AccountInfo]=None

class SongQueryParameters(SimpleQueryParameters):
	song: str = ""
	album: str = ""
	artist: str = ""
	songIds: Optional[Iterable[int]]=None
	albumId: Optional[int]=None
	artistId: Optional[int]=None
