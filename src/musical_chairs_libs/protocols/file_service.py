from typing import Protocol
from typing import BinaryIO, IO

class FileService(Protocol):

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	) -> IO[bytes]:
		...

	def open_song(self, keyPath: str) -> BinaryIO:
		...

	def download_url(self, keyPath: str) -> str:
		...

	def delete_song(self, keyPath: str):
		...

	def song_absolute_path(self, keyPath: str) -> str:
		...