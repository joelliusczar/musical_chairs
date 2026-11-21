from typing import Any, Generic, TypeVar, Optional, Callable
from queue import SimpleQueue, Empty as EmptyException
from threading import Condition, RLock
from .lost_found import Lost
import threading
import typing

T = TypeVar("T")


class BlockingQueue(Generic[T]):

	def __init__(self, size: int, retryInterval: Optional[int]=None) -> None:
		self.size = size
		self.__queue__ = SimpleQueue[T]()
		self.__count__ = 0
		self.__count_lock__ = RLock()
		self.__condition__ = Condition()
		self.__local__ = threading.local()
		self.retryInterval = retryInterval

	def __set_count__(self, count: int = 0):
		with self.__count_lock__:
			self.__count__ = count

	def __decrement__(self):
		with self.__count_lock__:
			self.__count__ -= 1

	def __increment__(self):
		with self.__count_lock__:
			self.__count__ += 1

	def qsize(self) -> int:
		with self.__count_lock__:
			return self.__count__

	def __check_not_in_context__(self, op: str):
		if getattr(self.__local__, "contextDepth", 0) > 0:
			raise RuntimeError(
				f"Cannot call {op} while inside a delayed decrement get"
			)

	def __internal_get__(
		self,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> T:
		with self.__condition__:
			while self.qsize() < 1:
				if checkShouldRetry and not checkShouldRetry(self):
					raise TimeoutError("Cannot wait for get any longer")
				self.__condition__.wait(self.retryInterval)
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
		self.__check_not_in_context__("get")
		item = self.__internal_get__(checkShouldRetry)
		self.__unblock_after_get__()
		return item

	def delayed_decrement_get(
		self,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> "DelayedDecrementReader[T]":
		self.__check_not_in_context__("delayed_decrement_get")
		return DelayedDecrementReader(self, checkShouldRetry)

	def drain(self) -> typing.List[T]:
		self.__check_not_in_context__("drain")
		items: typing.List[T] = []
		with self.__condition__:
			try:
				while True:
					item = self.__queue__.get(block=False)
					items.append(item)
			except EmptyException:
				pass
			self.__set_count__()
			self.__condition__.notify()
		return items

	def put(self,
		item: T,
		checkShouldRetry: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	):
		self.__check_not_in_context__("put")
		with self.__condition__:
			while self.qsize() >= self.size:
				if checkShouldRetry and not checkShouldRetry(self):
					raise TimeoutError("Cannot wait for put any longer")
				self.__condition__.wait(self.retryInterval)
			self.__queue__.put(item)
			self.__increment__()
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
		try:
			contextDepth = getattr(self.__queue__.__local__, "contextDepth", 0)
			self.__queue__.__local__.contextDepth = contextDepth + 1
			self.__item__ = self.__queue__.__internal_get__(self.__check_should_retry__)
			return self.__item__
		except:
			self.__queue__.__local__.contextDepth -= 1
			raise

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		try:
			if self.__item__ != Lost():
				self.__queue__.__unblock_after_get__()
		finally:
			self.__queue__.__local__.contextDepth -= 1