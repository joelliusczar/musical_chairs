####### This file is generated. #######
# edit regen_file_reference_file #
# in mc_dev_ops.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"001.grant_api.sql",
		"36195c78a8f001f617954ca94fa1467d667eadc00e97786e088d2f5b487e6c12"
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
		"b389086e4fd53da68499fc83bb97f92bf72ec0c44be3be9313979aaefcd7a7cd"
	)
	ADD_IP4ADDRESS = (
		"011.add_ip4address.sql",
		"4c44d1a57369986eafa90ba20202114b40f3ad0e1d4356d785bd64809c13bb08"
	)
	ADD_IP6ADDRESS = (
		"012.add_ip6address.sql",
		"4901552b86eed5dc5226516c9ca12146fe801bc79a5cb02fe779760ec74d21e6"
	)
	ADD_USERAGENT_FK = (
		"013.add_useragent_fk.sql",
		"8444071f34a7fe908125f3778a6b71261f8736121b3d5db28949aff0dd06cfcf"
	)
	TRIM_STATION_QUEUE_HISTORY = (
		"runtime/trim_station_queue_history.sql",
		"f3bac0c5e9b629edd5e96d3bcfff914649ba541408e450e13dcb254143c2186b"
	)

	@property
	def file_name(self) -> str:
		return self.value[0]

	@property
	def checksum(self) -> str:
		return self.value[1]
