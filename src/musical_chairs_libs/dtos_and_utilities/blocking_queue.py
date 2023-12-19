from typing import Generic, TypeVar, Optional, Callable
from queue import SimpleQueue, Empty as EmptyException
from threading import Condition, RLock

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

	def get(
		self,
		shouldContinue: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	) -> T:
		while self.qsize() < 1:
			with self.__condition__:
				self.__condition__.wait(self.retryInterval)
				if shouldContinue and not shouldContinue(self):
					raise TimeoutError("Cannot wait for get any longer")
		item = self.__queue__.get()
		self.__decrement__()
		with self.__condition__:
			self.__condition__.notify()
		return item
	
	def unblocked_get(self) -> Optional[T]:
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
		shouldContinue: Optional[Callable[["BlockingQueue[T]"], bool]]=None
	):
		while self.qsize() > self.size:
			with self.__condition__:
				self.__condition__.wait(self.retryInterval)
				if shouldContinue and not shouldContinue(self):
					raise TimeoutError("Cannot wait for put any longer")
		self.__queue__.put(item)
		self.__increment__()
		with self.__condition__:
			self.__condition__.notify()
			