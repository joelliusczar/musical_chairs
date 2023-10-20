from typing import BinaryIO
from musical_chairs_libs.services.saving import FileServiceBase

class MockFileService(FileServiceBase):

	def save_song(self, keyPath: str, file: BinaryIO):
		pass