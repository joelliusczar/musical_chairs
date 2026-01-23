from typing import (
	Iterable,
	Iterator,
	overload,
	Optional,
	Sequence,
	Union
)
from datetime import datetime, timedelta

class MockDatetimeProvider(Sequence[datetime]):

	def __init__(self, datetimes: Union[Iterable[datetime], datetime]) -> None:
		if isinstance(datetimes, Iterable):
			self.__iter_src__ = datetimes
			self.__dtIter__ = iter(datetimes)
			self.__current__ = next(self.__dtIter__)
		else:
			self.__current__ = datetimes
		self.__range__ = None


	def __next__(self) -> datetime:
		if self.__range__:
			try:
				next(self.__range__)
			except StopIteration:
				self.__range__ = None
				raise
		if self.__dtIter__:
			self.__current__ = next(self.__dtIter__)
		else:
			self.__current__ = self.__current__ + timedelta(microseconds=(1000))
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


	@overload
	def __getitem__(self, index: int) -> datetime:
		pass  # type checkers use this for type inference

	@overload
	def __getitem__(self, index: slice) -> Sequence[datetime]:
		pass  # type checkers use this for type inference

	def __getitem__(
		self,
		index: Union[int, slice]
	) -> Union[datetime, Sequence[datetime]]:
		if isinstance(index, slice):
			raise NotImplementedError("slice indexing not supported")
		if isinstance(self.__iter_src__, Sequence):
			return self.__iter_src__[index]
		elif not self.__dtIter__:
			return self.__current__ + timedelta(index * 1000)
		raise RuntimeError("Provider has no other implementations for getItem")


	def __len__(self) -> int:
		if isinstance(self.__iter_src__, Sequence):
			return len(self.__iter_src__)
		return 1


	def __contains__(self, item: object) -> bool:
		if isinstance(self.__iter_src__, Sequence):
			return item in self.__iter_src__
		return False


	def __str__(self) -> str:
		return  f"{str(self.__current__)}"


	def __repr__(self) -> str:
		return str(self)
