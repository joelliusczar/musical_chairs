import sys
import os
from typing import Any
from musical_chairs_libs.services import (
	EnvManager,
)
from .common_stream_helpers import (set_proc_id, unset_proc_id, get_song_info)
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
		print(display)
		songFullPath = f"{searchBase}/{songPath}"
		print(songFullPath)
		forward_data(songFullPath)
	unset_proc_id(stationId, dbName)

def begin_clean_up(signum: int, frame: Any):
	global isRunning
	isRunning = False

signal.signal(signal.SIGTERM, begin_clean_up)

