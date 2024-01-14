import hashlib
from pathlib import Path
from .env_manager import EnvManager
from .process_service import ProcessService
from musical_chairs_libs.dtos_and_utilities import SqlScripts


class TemplateService:

	def __init__(self) -> None:
		pass

	def __load_ices_config_template__(self) -> str:
		templateDir = EnvManager.templates_dir
		txt = Path(f"{templateDir}/ices.conf").read_text()
		return txt

	def __load_ices_python_module_template__(self) -> str:
		templateDir = EnvManager.templates_dir
		txt = Path(f"{templateDir}/template.py").read_text()
		return txt
	
	def __load_icecast_config_template__(self) -> str:
		templateDir = EnvManager.templates_dir
		txt = Path(f"{templateDir}/icecast.xml").read_text()
		return txt

	def __create_ices_config_content__(
		self,
		internalName: str,
		publicName: str,
		sourcePassword: str,
		username: str
	) -> str:
		icesConfigTemplate = self.__load_ices_config_template__()
		return icesConfigTemplate.replace(
			"<Password>icecast_password</Password>",
			f"<Password>{sourcePassword}</Password>"
		).replace(
			"<Module>internal_station_name</Module>",
			f"<Module>{username}_{internalName}</Module>"
		).replace(
			"<Mountpoint>/internal_station_name</Mountpoint>",
			f"<Mountpoint>/{username}/{internalName}</Mountpoint>"
		).replace(
			"<Name>public_station_name</Name>",
			f"<Name>{publicName}</Name>"
		)

	def __create_ices_python_module_content__(self, stationId: int) -> str:
		pythonModuleTemplate = self.__load_ices_python_module_template__()
		return pythonModuleTemplate.replace("<station_id>",str(stationId))

	def create_station_files(
		self,
		stationId: int,
		internalName: str,
		publicName: str,
		username: str
	):
		icecastConfLocation = ProcessService.get_icecast_conf_location()
		sourcePassword = EnvManager.read_config_value(
			icecastConfLocation,
			"source-password"
		)
		configContent = self.__create_ices_config_content__(
			internalName,
			publicName,
			sourcePassword,
			username
		)
		filename_base = f"{username}_{internalName}"
		Path(f"{EnvManager.station_config_dir}/ices.{filename_base}.conf")\
			.write_text(configContent)
		pythonModuleContent = self.__create_ices_python_module_content__(stationId)
		Path(f"{EnvManager.station_module_dir}/{filename_base}.py")\
			.write_text(pythonModuleContent)

	@staticmethod
	def load_sql_script_content(script: SqlScripts) -> str:
		sqlScriptsDir = EnvManager.sql_script_dir
		txt = Path(f"{sqlScriptsDir}/{script.file_name}").read_text()
		checksum = hashlib.md5(txt.encode("utf-8")).hexdigest()
		if checksum != script.checksum:
			raise RuntimeError(f"{script.file_name} is missing")
		return txt