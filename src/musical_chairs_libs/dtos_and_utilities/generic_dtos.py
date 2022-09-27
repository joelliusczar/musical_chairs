from typing import\
	List,\
	TypeVar,\
	Generic
from dataclasses import dataclass


T = TypeVar("T")

@dataclass()
class ListData(Generic[T]):
	items: List[T]

@dataclass()
class TableData(ListData[T]):
	totalRows: int


# class ErrorInfo(BaseModel):
# 	msg: str

@dataclass(frozen=True)
class IdItem:
	id: int