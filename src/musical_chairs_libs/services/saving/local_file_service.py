from typing import BinaryIO
from ..env_manager import EnvManager
from .file_service_protocol import FileServiceBase

class LocalFileService(FileServiceBase):

	def save_song(self, keyPath: str, file: BinaryIO):
		with open(f"{EnvManager.search_base}/{keyPath}", "wb") as out:
			for chunk in file:
				out.write(chunk)
