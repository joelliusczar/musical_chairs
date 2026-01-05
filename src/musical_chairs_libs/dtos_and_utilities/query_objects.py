from .generic_dtos import (
	MCBaseClass,
)
from pydantic import ConfigDict
from sqlalchemy import ColumnElement
from typing import Any, Iterable, Optional, Union

class SimpleQueryParameters(MCBaseClass):
	model_config = ConfigDict(arbitrary_types_allowed=True)
	page: int = 0
	limit: Optional[int]=None
	orderby: Optional[str]=None
	sortdir: Optional[str]=None 
	orderByElement: Union[ColumnElement[Any], str, None]=None

class SongQueryParameters(SimpleQueryParameters):
	song: str = ""
	album: str = ""
	artist: str = ""
	songIds: Optional[Iterable[int]]=None
	albumId: Optional[int]=None
	artistId: Optional[int]=None
