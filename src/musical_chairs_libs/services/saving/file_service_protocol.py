from typing import Protocol
from typing import BinaryIO

class FileServiceBase(Protocol):

	def save_song(self, keyPath: str, file: BinaryIO):
		pass