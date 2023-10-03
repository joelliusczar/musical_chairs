####### This file is generated. #######
# edit regen_file_reference_file #
# in radio_common.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"1.grant_api.sql",
		"90d1c67e87696c293f35422345031cc3"
	)
	GRANT_RADIO = (
		"2.grant_radio.sql",
		"6343c805d18243903058480d29fb1a75"
	)
	PATH_USER_INDEXES = (
		"3.path_user_indexes.sql",
		"7b01c84a4a8d756a7f952b2d5c382e33"
	)

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]
