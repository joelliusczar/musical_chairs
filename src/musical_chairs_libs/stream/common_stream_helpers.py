import sys
from typing import Tuple, Union, Optional
from musical_chairs_libs.services import (
	EnvManager,
	QueueService,
	StationService
)
import struct

def set_proc_id(
	stationId: int,
	dbName: str
):
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		StationService(conn).set_station_proc(stationId=stationId)
		conn.commit()
	finally:
		conn.close()

def unset_proc_id(
	stationId: int,
	dbName: str
):
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		StationService(conn)\
			.unset_station_procs(stationIds=stationId)
		conn.commit()
	finally:
		conn.close()

def get_song_info(
	stationId: int,
	dbName: str
) -> Tuple[str, Union[str,None], Union[str,None], Union[str,None]]:
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		queueService = QueueService(conn)
		(songPath, songName, album, artist) = \
			queueService.pop_next_queued(stationId=stationId)
		return songPath, songName, album, artist
	finally:
		conn.close()

def get_station_id(
	stationName: str,
	ownerName: str,
	dbName: str
) -> Optional[int]:
	conn = EnvManager.get_configured_radio_connection(dbName)
	try:
		stationId = StationService(conn).get_station_id(stationName, ownerName)
		return stationId
	finally:
		conn.close()


def send_size_packet(size: int):
	sizePacket = struct.pack("i", size)
	sys.stdout.buffer.write(sizePacket)