from typing import\
	List,\
	TypeVar,\
	Generic
from pydantic import BaseModel as MCBaseClass, ConfigDict


T = TypeVar("T")

class FrozenBaseClass(MCBaseClass):
	model_config = ConfigDict(frozen=True)

class ListData(MCBaseClass, Generic[T]):
	items: List[T]


class TableData(ListData[T]):
	totalrows: int


# class ErrorInfo(BaseModel):
# 	msg: str

class IdItem(FrozenBaseClass):
	id: int