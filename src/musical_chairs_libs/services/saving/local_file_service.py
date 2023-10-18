#pyright: reportMissingTypeStubs=false
from pathlib import Path
from typing import BinaryIO
from ..env_manager import EnvManager
from .file_service_protocol import FileServiceBase


class LocalFileService(FileServiceBase):

	def __create_missing_directories__(self, keyPath: str):
		savedPath = f"{EnvManager.search_base}/{keyPath}"
		path = Path(savedPath)
		path.parents[0].mkdir(parents=True, exist_ok=True)

	# def extract_song_info(self, file: BinaryIO):
	# 	try:
	# 		tag = TinyTag.get(file_obj=file) #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
	# 		pass
	# 	except Exception as e:
	# 		pass


	def save_song(self, keyPath: str, file: BinaryIO):
		self.__create_missing_directories__(keyPath)
		savedPath = f"{EnvManager.search_base}/{keyPath}"
		with open(savedPath, "wb") as out:
			for chunk in file:
				out.write(chunk)
