from typing import Any, Generic, TypeVar, Optional, Callable
from queue import SimpleQueue, Empty as EmptyException
from threading import Condition, RLock
from .lost_found import Lost

T = TypeVar("T")

class BlockingQueue(Generic[T]):

	def __init__(self, size: int, retryInterval: Optional[int]=None) -> None:
		self.size = size
		self.__queue__ = SimpleQueue[T]()
		self.__count__ = 0
		self.__count_lock__ = RLock()
		self.__condition__ = Condition()
		self.retryInterval = retryInterval

	def __decrement__(self):
		with self.__count_lock__:
			self.__count__ -= 1

	def __increment__(self):
		with self.__count_lock__:
			self.__count__ += 1

	def qsize(self) -> int:
		with self.__count_lock__:
			return self.__count__

	def __get__(
		self,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> T:
		while self.qsize() < 1:
			with self.__condition__:
				self.__condition__.wait(self.retryInterval)
				if checkShouldRetry and not checkShouldRetry(self):
					raise TimeoutError("Cannot wait for get any longer")
		item = self.__queue__.get()
		return item

	def __unblock_after_get__(self):
		self.__decrement__()
		with self.__condition__:
			self.__condition__.notify()

	def get(
		self,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> T:
		item = self.__get__(checkShouldRetry)
		self.__unblock_after_get__()
		return item

	def delayed_decrement_get(
		self,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> "DelayedDecrementReader[T]":
		return DelayedDecrementReader(self, checkShouldRetry)

	def get_unblocked(self) -> Optional[T]:
		try:
			item = self.__queue__.get(block=False)
			self.__decrement__()
			with self.__condition__:
				self.__condition__.notify()
			return item
		except EmptyException:
			return None

	def put(self,
		item: T,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	):
		while self.qsize() >= self.size:
			with self.__condition__:
				self.__condition__.wait(self.retryInterval)
				if checkShouldRetry and not checkShouldRetry(self):
					raise TimeoutError("Cannot wait for put any longer")
		self.__queue__.put(item)
		self.__increment__()
		with self.__condition__:
			self.__condition__.notify()

class DelayedDecrementReader(Generic[T]):

	def __init__(
		self,
		queue: "BlockingQueue[T]",
		shouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> None:
		self.__queue__ = queue
		self.__check_should_retry__ = shouldRetry
		self.__item__ = Lost()

	def __enter__(
		self,
	) -> T:
		self.__item__ = self.__queue__.__get__(self.__check_should_retry__)
		return self.__item__

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		if self.__item__ != Lost():
			self.__queue__.__unblock_after_get__()