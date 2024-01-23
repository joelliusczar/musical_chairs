from typing import Protocol
from typing import BinaryIO
from musical_chairs_libs.dtos_and_utilities import SongAboutInfo

class FileServiceBase(Protocol):

	def save_song(self, keyPath: str, file: BinaryIO) -> SongAboutInfo:
		...

	def open_song(self, keyPath: str) -> BinaryIO:
		...

	def download_url(self, keyPath: str) -> str:
		...
