import sys
from .queue_song_source import load_data, send_next
from typing import (
	Any
)
from musical_chairs_libs.services import (
	ProcessService
)
from asyncio import (
	get_event_loop, 
	gather,
	Task
)

background_tasks: set[Task[Any]] = set()




def start_song_queue(dbName: str, stationName: str, ownerName: str):
	def handle_send_next_close(task: Task[Any]):
		background_tasks.discard(task)
		loadTask.cancel()

	def start_ices(portNumber: str):
		ProcessService.start_station_mc_ices(stationName, ownerName, portNumber)

	try:
		loop = get_event_loop()
		loadTask = loop.create_task(load_data(dbName, stationName, ownerName))
		sendTask = loop.create_task(send_next(start_ices))

		background_tasks.add(loadTask)
		background_tasks.add(sendTask) 

		loadTask.add_done_callback(background_tasks.discard)
		sendTask.add_done_callback(handle_send_next_close)

		

		loop.run_until_complete(gather(loadTask, sendTask))
	except Exception:
		
		for t in background_tasks:
			t.cancel()
		raise




if __name__ == "__main__":
	dbName = sys.argv[1]
	stationName = sys.argv[2]
	ownerName = sys.argv[3]


	start_song_queue(dbName, stationName, ownerName)
