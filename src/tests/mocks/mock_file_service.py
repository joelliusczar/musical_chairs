from typing import BinaryIO
from io import BytesIO
from musical_chairs_libs.services.fs import FileServiceBase

class MockFileService(FileServiceBase):

	def save_song(self, keyPath: str, file: BinaryIO):
		pass

	def open_song(self, keyPath: str) -> BinaryIO:
		return BytesIO(b"Howdy")
	
	def download_url(self, keyPath: str) -> str:
		return keyPath