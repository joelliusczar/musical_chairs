from typing import (
	Any,
	TypeVar,
	Union
)
from collections import UserDict

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class IdDict(UserDict[TKey, TValue]):
	
	def __init__(self, id: Union[int, str], initialData: dict[TKey, TValue]):
		self.id = id
		self.data = initialData

	def __hash__(self) -> int:
		return hash(self.id)
	
	def __eq__(self, other: Any) -> bool:
		return self.id == other.id
