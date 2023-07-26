from pathlib import Path
import re
from .env_manager import EnvManager


class TemplateService:

	def _load_ices_config_template(self) -> str:
		templateDir = EnvManager.templates_dir
		txt = Path(f"{templateDir}/ices.conf").read_text()
		return txt

	def _load_ices_python_module_template(self) -> str:
		templateDir = EnvManager.templates_dir
		txt = Path(f"{templateDir}/template.py").read_text()
		return txt

	def __extract_icecast_source_password__(self) -> str:
		icecasetConfLocation = EnvManager.icecast_conf_location
		passLines: list[str] = []
		with open(icecasetConfLocation, "r") as icecast_config:
			for line in icecast_config:
				if "<source-password>" in line or passLines:
					passLines.append(line)
				if "</source-password>" in line:
					break
		segment = "".join(passLines)
		match = re.search(r"<source-password>(\w+)</source-password>", segment)
		if match:
			g = match.groups()
			return g[0]
		return ""


	def __create_ices_config_content__(
		self,
		internalName: str,
		publicName: str,
		sourcePassword: str,
		username: str
	) -> str:
		icesConfigTemplate = self._load_ices_config_template()
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
		pythonModuleTemplate = self._load_ices_python_module_template()
		return pythonModuleTemplate.replace("<station_id>",str(stationId))

	def create_station_files(
		self,
		stationId: int,
		internalName: str,
		publicName: str,
		username: str
	):
		sourcePassword = self.__extract_icecast_source_password__()
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