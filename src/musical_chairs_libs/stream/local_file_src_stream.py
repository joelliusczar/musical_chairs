import sys
import os
from typing import Any
from musical_chairs_libs.services import (
	EnvManager,
)
from musical_chairs_libs.dtos_and_utilities import (
	format_newlines_for_stream
)
from .common_stream_helpers import (
	set_proc_id,
	unset_proc_id,
	get_song_info,
	send_size_packet
)
import signal


isRunning: bool = False

def forward_data(songFullPath: str):
	with open(songFullPath, "rb") as songFile:
		while True:
			b = songFile.read(4096)
			if b:
				sys.stdout.buffer.write(b)
			else:
				break


def send_data(
	stationId: int,
	dbName: str
):
	set_proc_id(stationId, dbName)
	global isRunning
	isRunning = True
	while isRunning:
		searchBase = EnvManager.search_base
		(songPath, songName, album, artist) = \
			get_song_info(stationId, dbName)
		if songName:
			display = f"{songName} - {album} - {artist}"
		else:
			display = os.path.splitext(os.path.split(songPath)[1])[0]
		sys.stdout.buffer.write(format_newlines_for_stream(display).encode())
		songFullPath = f"{searchBase}/{songPath}"
		sys.stdout.buffer.write(format_newlines_for_stream(songFullPath).encode())
		size = os.path.getsize(songFullPath)
		send_size_packet(size)
		forward_data(songFullPath)
	unset_proc_id(stationId, dbName)

def begin_clean_up(signum: int, frame: Any):
	global isRunning
	sys.stderr.buffer.write(b"We have recieved the signall to end")
	isRunning = False

signal.signal(signal.SIGTERM, begin_clean_up)