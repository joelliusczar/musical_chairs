from typing import Generic, TypeVar, Optional
from queue import SimpleQueue, Empty as EmptyException
from threading import Condition, RLock

T = TypeVar("T")

class BlockingQueue(Generic[T]):

	def __init__(self, size: int) -> None:
		self.size = size
		self.__queue__ = SimpleQueue[T]()
		self.__count__ = 0
		self.__count_lock__ = RLock()
		self.__condition__ = Condition()

	def __decrement__(self):
		with self.__count_lock__:
			self.__count__ -= 1

	def __increment__(self):
		with self.__count_lock__:
			self.__count__ += 1

	def qsize(self) -> int:
		with self.__count_lock__:
			return self.__count__

	def get(self, timeout: Optional[int]=None) -> T:
		while self.qsize() < 1:
				print(f"wait for queue to have item{self.qsize()}")
				with self.__condition__:
					self.__condition__.wait(timeout)
		item = self.__queue__.get()
		self.__decrement__()
		with self.__condition__:
			self.__condition__.notify()
		return item
	
	def put(self, item: T, timeout: Optional[int]=None):
		while self.qsize() > self.__count__:
			print(f"wait for queue to be empty {self.qsize()}")
			with self.__condition__:
				self.__condition__.wait(timeout)
		self.__queue__.put(item)
		self.__increment__()
		with self.__condition__:
			self.__condition__.notify()
			