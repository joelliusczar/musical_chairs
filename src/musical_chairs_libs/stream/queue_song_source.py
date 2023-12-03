import sys
import os
import socket
from typing import (
	Tuple,
	Union,
	Iterator,
	BinaryIO,
	Optional,
	cast,
	Callable
)
# from musical_chairs_libs.services import (
# 	EnvManager,
# 	QueueService
# )
from tempfile import NamedTemporaryFile
from asyncio import Queue

queue = Queue[Tuple[Optional[BinaryIO], Optional[str]]](3)




def get_song_info(
	stationId: int,
	dbName: str
) -> Iterator[
		Tuple[str, Union[str,None]]
	]:
	yield ("./safety_in", "Safety")
	yield ("./input_file", "Jesu")
	yield ("./safety_in", "Safety")
	yield ("./input_file", "Jesu")
	yield ("./safety_in", "Safety")


	# while True:
	# 	conn = EnvManager.get_configured_radio_connection(dbName)
	# 	try:
	# 		queueService = QueueService(conn)
	# 		(songPath, songName, album, artist) = \
	# 			queueService.pop_next_queued(stationId=stationId)
	# 		if songName:
	# 			display = f"{songName} - {album} - {artist}"
	# 		else:
	# 			display = os.path.splitext(os.path.split(songPath)[1])[0]
	# 		yield songPath, display
	# 	except:
	# 		break
	# 	finally:
	# 		conn.close()

# def get_station_id(
# 	stationName: str,
# 	ownerName: str,
# 	dbName: str
# ) -> Optional[int]:
# 	conn = EnvManager.get_configured_radio_connection(dbName)
# 	try:
# 		stationId = StationService(conn).get_station_id(stationName, ownerName)
# 		return stationId
# 	finally:
# 		conn.close()

async def load_data(dbName: str, stationName: str, ownerName: str):
	# stationId = get_station_id(stationName, ownerName, dbName)
	# if not stationId:
	# 	raise RuntimeError(
	# 		"station with owner"
	# 		f" {ownerName} and name {stationName} not found"
	# 	)
	stationId = 0
	currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
	for (filename, display) in get_song_info(stationId, dbName):
		await queue.put((currentFile, display))
		with open(filename, "rb") as src:
			for chunk in src:
				currentFile.write(chunk)
		currentFile = cast(BinaryIO, NamedTemporaryFile(mode="wb"))
	await queue.put((None, None))

async def send_next(onAddressBind: Callable[[str], None]):
	currentFile = None
	host = "127.0.0.1"
	portNumber = 50009
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		# listener.settimeout(5)
		listener.bind((host, portNumber))
		listener.listen(1)
		onAddressBind(str(listener.getsockname()[1]))
		conn, _ = listener.accept()
		with conn:
			while True:
				res = conn.recv(1)
				if res == b"0":
					break
				if currentFile:
					currentFile.close()
				currentFile, display = await queue.get()
				if currentFile:
					conn.sendall(f"{currentFile.name}\n".encode())
					conn.sendall(f"{display}\n".encode())
				else:
					conn.sendall(b"")
					break
	except BrokenPipeError:
		devnull = os.open(os.devnull, os.O_WRONLY)
		os.dup2(devnull, sys.stdout.fileno())
	finally:
		listener.shutdown(socket.SHUT_RD)
		listener.close()


