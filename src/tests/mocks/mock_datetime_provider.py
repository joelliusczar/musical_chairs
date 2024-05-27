from typing import (Iterable, Iterator, overload, Optional, Union)
from datetime import datetime

class MockDatetimeProvider:

	def __init__(self, datetimes: Iterable[datetime]) -> None:
		self.__dtIter__ = iter(datetimes)
		self.__range__ = None
		self.__current__ = next(self.__dtIter__)

	def __next__(self) -> datetime:
		if self.__range__:
			try:
				next(self.__range__)
			except StopIteration:
				self.__range__ = None
				raise
		self.__current__ = next(self.__dtIter__)
		return self.__current__



	def __iter__(self) -> Iterator[datetime]:
		return self

	@overload
	def __call__(self) -> datetime: ...

	@overload
	def __call__(self, offset: Optional[int]) -> Iterator[datetime]: ...

	def __call__(
		self,
		offset: Optional[int]=None
	) -> Union[datetime, Iterator[datetime]]:
		if offset != None:
			self.__range__ = iter(range(offset))
			return self

		return self.__current__

	def __str__(self) -> str:
		return  f"{str(self.__current__)}"

	def __repr__(self) -> str:
		return str(self)
