from typing import Protocol
from typing import BinaryIO

class FileService(Protocol):

	def save_song(self,
		keyPath: str,
		file: BinaryIO
	) -> BinaryIO:
		...

	def open_song(self, keyPath: str) -> BinaryIO:
		...

	def download_url(self, keyPath: str) -> str:
		...

	def delete_song(self, keyPath: str):
		...