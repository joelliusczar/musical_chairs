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

