from typing import\
	List,\
	TypeVar,\
	Generic
from pydantic import BaseModel


T = TypeVar("T")

class ListData(BaseModel, Generic[T]):
	items: List[T]

class TableData(ListData[T]):
	totalRows: int


class ErrorInfo(BaseModel):
	msg: str

