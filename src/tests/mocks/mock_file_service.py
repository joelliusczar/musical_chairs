from typing import BinaryIO, Tuple
from io import BytesIO
from musical_chairs_libs.dtos_and_utilities import SongAboutInfo
from musical_chairs_libs.protocols import FileService

class MockFileService(FileService):

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	) -> Tuple[SongAboutInfo, bytes]:
		if keyPath:
			segments = keyPath.split("/")
			return \
				SongAboutInfo(name=next((s for s in segments),"")),\
				keyPath.encode("utf-8")
		return SongAboutInfo(name=""), keyPath.encode("utf-8")

	def open_song(self, keyPath: str) -> BinaryIO:
		return BytesIO(keyPath.encode("utf-8"))

	def download_url(self, keyPath: str) -> str:
		return keyPath