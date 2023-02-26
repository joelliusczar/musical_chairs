from typing import (Iterable, Iterator, overload, Optional, Union)
from datetime import datetime, timedelta

class MockDatetimeProvider:

	def __init__(self, datetimes: Iterable[datetime]) -> None:
		self.datetimes = list(datetimes)
		#using index tracking so it's easier to see where I am while testing
		self.idx = 0
		self.__range_to = None
		self.__current = self.datetimes[self.idx]
		self.__latest = self.__current
		self.__time_offset = timedelta()

	def __next__(self) -> datetime:
		if self.__range_to != None:
			if self.idx >= self.__range_to:
				self.__range_to = None
				raise StopIteration()
		self.__current = self.datetimes[self.idx]
		self.idx += 1
		return self.__current

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
			self.__range_to = self.idx + offset
			return self

		self.__latest = self.__current + self.__time_offset

		return self.__latest

	def __str__(self) -> str:
		return  f"idx: {self.idx} - {str(self.__latest)}"

	def __repr__(self) -> str:
		return str(self)
