from typing import Union, TypeVar

class Sentinel:

	def __init__(self, value: bool) -> None:
		self.value = value

	def __bool__(self) -> bool:
		return self.value

	def __repr__(self) -> str:
		return "found" if self else "missing"

missing = Sentinel(False)
found = Sentinel(True)

T = TypeVar("T")

MCOptional = Union[T, Sentinel]