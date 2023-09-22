####### This file is generated. #######
# edit regen_file_reference_file #
# in radio_common.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = ("1.grant_api.sql", "a702d64bb28732a43e066a74436a07ce")
	GRANT_RADIO = ("2.grant_radio.sql", "5fadbff579330252b89b7e31b831c616")

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]

