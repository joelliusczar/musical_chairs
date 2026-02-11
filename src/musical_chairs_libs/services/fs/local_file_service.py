#pyright: reportMissingTypeStubs=false
from pathlib import Path
from typing import BinaryIO
from musical_chairs_libs.protocols import FileService
from musical_chairs_libs.dtos_and_utilities import ConfigAcessors


class LocalFileService(FileService):

	def __create_missing_directories__(self, keyPath: str):
		savedPath = f"{ConfigAcessors.absolute_content_home()}/{keyPath}"
		path = Path(savedPath)
		path.parents[0].mkdir(parents=True, exist_ok=True)


	def save_song(self,
		keyPath: str,
		file: BinaryIO
	):
		self.__create_missing_directories__(keyPath)
		savedPath = f"{ConfigAcessors.absolute_content_home()}/{keyPath}"
		with open(savedPath, "wb") as out:
			for chunk in file:
				out.write(chunk)


	def open_song(self, keyPath: str) -> BinaryIO:
		return open(keyPath, "rb")

	def download_url(self, keyPath: str) -> str:
		return keyPath

	def delete_song(self, keyPath: str):
		path = Path(keyPath)
		path.unlink()

	def song_absolute_path(self, keyPath: str) -> str:
		return f"{ConfigAcessors.absolute_content_home()}/{keyPath}"