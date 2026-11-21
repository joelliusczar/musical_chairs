import threading
import pytest
from musical_chairs_libs.dtos_and_utilities import (
	BlockingQueue
)

def test_add_and_get():
	queue = BlockingQueue[str](4, 3)
	assert queue.qsize() == 0
	with pytest.raises(TimeoutError):
		queue.get(lambda _ : False)
	queue.put("alpha")
	assert queue.qsize() == 1
	with queue.delayed_decrement_get() as item:
		assert item == "alpha"
		assert queue.qsize() == 1
	assert queue.qsize() == 0
	with pytest.raises(TimeoutError):
		queue.get(lambda _ : False)


def test_ops_on_fresh_queue_from_fresh_thread():
	queue = BlockingQueue[int](3, 1)
	errors: list[BaseException] = []

	def worker():
		try:
			queue.put(1)
			assert queue.get() == 1
			assert queue.drain() == []
		except BaseException as e:
			errors.append(e)

	t = threading.Thread(target=worker)
	t.start()
	t.join(5)
	assert not t.is_alive()
	assert errors == []


def test_sequential_delayed_decrement_gets_then_drain():
	queue = BlockingQueue[int](3, 1)
	queue.put(1)
	queue.put(2)
	queue.put(3)
	with queue.delayed_decrement_get() as a:
		assert a == 1
	with queue.delayed_decrement_get() as b:
		assert b == 2
	assert queue.qsize() == 1
	assert queue.drain() == [3]
	assert queue.qsize() == 0
	queue.put(4)
	assert queue.get() == 4


def test_queue_ops_inside_delayed_get_raise():
	queue = BlockingQueue[int](3, 1)
	queue.put(1)
	queue.put(2)
	with queue.delayed_decrement_get() as item:
		assert item == 1
		with pytest.raises(RuntimeError):
			queue.get()
		with pytest.raises(RuntimeError):
			queue.put(5)
		with pytest.raises(RuntimeError):
			queue.drain()
		with pytest.raises(RuntimeError):
			queue.delayed_decrement_get()
	#guard is released once the context exits
	assert queue.get() == 2
	queue.put(3)
	assert queue.drain() == [3]


def test_exception_in_body_releases_guard_and_decrements():
	queue = BlockingQueue[int](3, 1)
	queue.put(1)
	with pytest.raises(ValueError):
		with queue.delayed_decrement_get():
			raise ValueError("boom")
	assert queue.qsize() == 0
	queue.put(2)
	assert queue.get() == 2


def test_timeout_on_enter_releases_guard():
	queue = BlockingQueue[int](3, 1)
	with pytest.raises(TimeoutError):
		with queue.delayed_decrement_get(lambda _ : False):
			pass
	assert queue.qsize() == 0
	#would raise RuntimeError if the depth leaked
	queue.put(1)
	with queue.delayed_decrement_get() as item:
		assert item == 1
	assert queue.drain() == []


def test_other_thread_can_put_while_reader_waits():
	queue = BlockingQueue[int](3, 1)
	received: list[int] = []
	errors: list[BaseException] = []

	def reader():
		try:
			with queue.delayed_decrement_get() as item:
				received.append(item)
		except BaseException as e:
			errors.append(e)

	t = threading.Thread(target=reader)
	t.start()
	#give the reader time to enter the context and start waiting
	t.join(0.2)
	assert t.is_alive()
	queue.put(7)
	t.join(5)
	assert not t.is_alive()
	assert errors == []
	assert received == [7]
	assert queue.qsize() == 0


def test_other_thread_can_put_while_reader_holds_item():
	queue = BlockingQueue[int](3, 1)
	queue.put(1)
	errors: list[BaseException] = []

	def producer():
		try:
			queue.put(2)
		except BaseException as e:
			errors.append(e)

	with queue.delayed_decrement_get() as item:
		assert item == 1
		t = threading.Thread(target=producer)
		t.start()
		t.join(5)
		assert not t.is_alive()
		#held item still counts until the context exits
		assert queue.qsize() == 2
	assert errors == []
	assert queue.qsize() == 1
	assert queue.get() == 2


def test_drain_keeps_falsy_items_and_unblocks_put():
	queue = BlockingQueue[int](2, 1)
	queue.put(0)
	queue.put(5)
	done = threading.Event()

	def producer():
		queue.put(9)
		done.set()

	t = threading.Thread(target=producer)
	t.start()
	assert not done.wait(0.2) #blocked: queue is full
	assert queue.drain() == [0, 5]
	assert done.wait(5)
	t.join(5)
	assert queue.qsize() == 1
	assert queue.get() == 9
