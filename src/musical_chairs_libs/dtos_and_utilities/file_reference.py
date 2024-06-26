####### This file is generated. #######
# edit regen_file_reference_file #
# in radio_common.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"1.grant_api.sql",
		"dd79707fb19fbe3dc63cbc6018ecde0d"
	)
	GRANT_RADIO = (
		"2.grant_radio.sql",
		"2b66091251d726783ab8f74164ce8045"
	)
	PATH_USER_INDEXES = (
		"3.path_user_indexes.sql",
		"99af0f60fa4053868f14f2488f81337c"
	)
	NEXT_DIRECTORY_LEVEL = (
		"4.next_directory_level.sql",
		"a3c3878db54ff3188091f51d50578e6f"
	)
	NORMALIZE_OPENING_SLASH = (
		"5.normalize_opening_slash.sql",
		"d2946254f45be36bdb565f398034c5a1"
	)
	DROP_REQUESTED_TIMESTAMP = (
		"6.drop_requested_timestamp.sql",
		"366ec48ec490f9e56d61d06838d6809b"
	)

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]
