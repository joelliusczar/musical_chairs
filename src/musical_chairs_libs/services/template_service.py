import hashlib
import re
from pathlib import Path
from .process_service import ProcessService
from musical_chairs_libs import SqlScripts
from musical_chairs_libs.dtos_and_utilities import ConfigAcessors


class TemplateService:

	def __init__(self) -> None:
		pass

	def __load_ices_config_template__(self) -> str:
		templateDir = ConfigAcessors.templates_dir()
		txt = Path(f"{templateDir}/ices.conf").read_text()
		return txt

	def __load_ices_python_module_template__(self) -> str:
		templateDir = ConfigAcessors.templates_dir()
		txt = Path(f"{templateDir}/template.py").read_text()
		return txt
	
	def __load_icecast_config_template__(self) -> str:
		templateDir = ConfigAcessors.templates_dir()
		txt = Path(f"{templateDir}/icecast.xml").read_text()
		return txt

	def __create_ices_config_content__(
		self,
		internalName: str,
		publicName: str,
		sourcePassword: str,
		username: str,
		bitrate: int=128
	) -> str:
		icesConfigTemplate = self.__load_ices_config_template__()
		return icesConfigTemplate.replace(
			"<Password>icecast_password</Password>",
			f"<Password>{sourcePassword}</Password>"
		).replace(
			"<Module>internal_station_name</Module>",
			"<Module>station</Module>"
		).replace(
			"<Mountpoint>/internal_station_name</Mountpoint>",
			f"<Mountpoint>/{username}/{internalName}</Mountpoint>"
		).replace(
			"<Name>public_station_name</Name>",
			f"<Name>{publicName}</Name>"
		).replace(
			"<Bitrate>128</Bitrate>",
			f"<Bitrate>{bitrate}</Bitrate>"
		)

	def __create_ices_python_module_content__(self, stationId: int) -> str:
		pythonModuleTemplate = self.__load_ices_python_module_template__()
		return pythonModuleTemplate.replace("<station_id>",str(stationId))



	def station_config_path(
		self, 
		internalName: str, 
		username: str
	) -> Path:
		filename_base = f"{username}_{internalName}"
		ices_filename = f"ices.{filename_base}.conf"
		return Path(f"{ConfigAcessors.station_config_dir()}/{ices_filename}")


	def does_station_config_exist(
		self, 
		internalName: str, 
		username: str
	) -> bool:
		return self.station_config_path(internalName, username).exists()

	def load_station_config_contents(
		self, 
		internalName: str, 
		username: str
	) -> str:
		return self.station_config_path(internalName, username).read_text()
	

	def sync_station_password(
		self, 
		internalName: str, 
		username: str
	):
		sourcePassword = self.extract_icecast_password()
		configContent = self.load_station_config_contents(internalName, username)
		if sourcePassword not in configContent:
			updatedContent = re.sub(
				r"<Password>.*</Password>",
				f"<Password>{sourcePassword}</Password>",
				configContent
			)
			self.station_config_path(internalName, username)\
				.write_text(updatedContent)

	def create_station_files(
		self,
		stationId: int,
		internalName: str,
		publicName: str,
		username: str,
		bitrate: int=128
	):
		sourcePassword = self.extract_icecast_password()
		configContent = self.__create_ices_config_content__(
			internalName,
			publicName,
			sourcePassword,
			username,
			bitrate
		)
		self.station_config_path(internalName, username).write_text(configContent)


	@staticmethod
	def extract_icecast_password():
			icecastConfLocation = ProcessService.get_icecast_conf_location()
			return ConfigAcessors.read_config_value(
				icecastConfLocation,
				"source-password"
			)

	@staticmethod
	def load_sql_script_content(script: SqlScripts) -> str:
		sqlScriptsDir = ConfigAcessors.sql_script_dir()
		txt = Path(f"{sqlScriptsDir}/{script.file_name}").expanduser().read_text()
		checksum = hashlib.sha256(txt.encode("utf-8")).hexdigest()
		if checksum != script.checksum:
			raise RuntimeError(f"{script.file_name} is missing")
		return txt
	
