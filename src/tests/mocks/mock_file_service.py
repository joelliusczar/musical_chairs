from typing import BinaryIO
from io import BytesIO
from musical_chairs_libs.dtos_and_utilities import SongAboutInfo
from musical_chairs_libs.protocols import FileService

class MockFileService(FileService):

	def save_song(self, keyPath: str, file: BinaryIO) -> SongAboutInfo:
		if keyPath:
			segments = keyPath.split("/")
			return SongAboutInfo(name=next((s for s in segments),""))
		return SongAboutInfo(name="")

	def open_song(self, keyPath: str) -> BinaryIO:
		return BytesIO(b"Howdy")
	
	def download_url(self, keyPath: str) -> str:
		return keyPath