####### This file is generated. #######
# edit regen_file_reference_file #
# in mc_dev_ops.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"001.grant_api.sql",
		"49e32f7b58a88e6b9c670e8135b2731369fac92b0875b5172b107019d0182ab8"
	)
	GRANT_RADIO = (
		"002.grant_radio.sql",
		"b47b5d523512386597a18b3ee5937befec75e01917e10916830a5ee836af3b44"
	)
	PATH_USER_INDEXES = (
		"003.path_user_indexes.sql",
		"aa2da440fb3a72855de2beeb08d37e778f9da92dd07ca20958fbb896d91841ca"
	)
	NEXT_DIRECTORY_LEVEL = (
		"004.next_directory_level.sql",
		"808f1932fbb6018957c634d89aaebada3ced8e36c24cb1746e249675c4b8e7c0"
	)
	NORMALIZE_OPENING_SLASH = (
		"005.normalize_opening_slash.sql",
		"a31b18b80e2230042abd20650f59829cef7ac16d7274f0eaca148dc04664ab75"
	)
	DROP_REQUESTED_TIMESTAMP = (
		"006.drop_requested_timestamp.sql",
		"b137be347d0dc64ca883d8a2d654640a3637ce98d6528451ed7709242c986349"
	)
	ADD_INTERNAL_PATH = (
		"007.add_internal_path.sql",
		"fc95eed4f25910b47309febf79fd57699a12a5d2457d661a92e4d2a92ca60952"
	)
	DROP_PLACEHOLDERDIR = (
		"008.drop_placeholderdir.sql",
		"3442e35cad725d451e0ff203d432e06b54b4a6651d658201c0001e1f8c38b7c9"
	)
	ADD_SONG_FILE_HASH = (
		"009.add_song_file_hash.sql",
		"9714741c4021d6a03c98b833d97f7a640733474f82f8f8b76365432dff7e6133"
	)
	GRANT_JANITOR = (
		"010.grant_janitor.sql",
		"4b16d6c39a9811afed82264b498ce49f64893cf1cb5987f4b97553a71ee7e924"
	)

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]
