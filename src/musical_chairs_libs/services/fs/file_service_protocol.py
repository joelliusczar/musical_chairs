from typing import Protocol
from typing import BinaryIO

class FileServiceBase(Protocol):

	def save_song(self, keyPath: str, file: BinaryIO):
		...

	def open_song(self, keyPath: str) -> BinaryIO:
		...

	def download_url(self, keyPath: str) -> str:
		...
