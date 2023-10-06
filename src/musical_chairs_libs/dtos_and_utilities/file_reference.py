####### This file is generated. #######
# edit regen_file_reference_file #
# in radio_common.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"1.grant_api.sql",
		"ad1c3e4900a58495fefb555708eeff79"
	)
	GRANT_RADIO = (
		"2.grant_radio.sql",
		"6343c805d18243903058480d29fb1a75"
	)
	PATH_USER_INDEXES = (
		"3.path_user_indexes.sql",
		"99af0f60fa4053868f14f2488f81337c"
	)
	NEXT_DIRECTORY_LEVEL = (
		"4.next_directory_level.sql",
		"385d3947b221f220e4a59b51b197f42a"
	)

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]
