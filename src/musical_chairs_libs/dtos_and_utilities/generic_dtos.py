from typing import (
	List,
	TypeVar,
	Generic
)
from pydantic import BaseModel as MCBaseClass, ConfigDict, Field


T = TypeVar("T")

class FrozenBaseClass(MCBaseClass):
	model_config = ConfigDict(frozen=True)

class ListData(MCBaseClass, Generic[T]):
	items: List[T]


class TableData(ListData[T]):
	totalrows: int


# class ErrorInfo(BaseModel):
# 	msg: str

class FrozenIdItem(FrozenBaseClass):
	id: int

class FrozenNamed(FrozenBaseClass):
	name: str

class FrozenNamedIdItem(FrozenIdItem, FrozenNamed):
	...


class IdItem(MCBaseClass):
	id: int=Field(frozen=True)

class Named(MCBaseClass):
	name: str=Field(frozen=True)

class NamedIdItem(IdItem, Named):
	...
