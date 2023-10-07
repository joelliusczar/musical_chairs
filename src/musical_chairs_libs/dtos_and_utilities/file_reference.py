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
		"4cbdc955359cbdbb9055f420bbf37912"
	)
	PATH_USER_INDEXES = (
		"3.path_user_indexes.sql",
		"99af0f60fa4053868f14f2488f81337c"
	)
	NEXT_DIRECTORY_LEVEL = (
		"4.next_directory_level.sql",
		"385d3947b221f220e4a59b51b197f42a"
	)
	NORMALIZE_OPENING_SLASH = (
		"5.normalize_opening_slash.sql",
		"d2946254f45be36bdb565f398034c5a1"
	)

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]
