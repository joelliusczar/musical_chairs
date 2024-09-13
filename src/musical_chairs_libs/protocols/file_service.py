from typing import Protocol
from typing import BinaryIO, Tuple
from musical_chairs_libs.dtos_and_utilities import SongAboutInfo

class FileService(Protocol):

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	) -> Tuple[SongAboutInfo, bytes]:
		...

	def open_song(self, keyPath: str) -> BinaryIO:
		...

	def download_url(self, keyPath: str) -> str:
		...

	def delete_song(self, keyPath: str):
		...