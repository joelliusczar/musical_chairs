####### This file is generated. #######
# edit regen_file_reference_file #
# in mc_dev_ops.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"001.grant_api.sql",
		"0735b8469b52ff581232a764470a961ee8919ab807488689a155c24b5df0d64d"
	)
	GRANT_RADIO = (
		"002.grant_radio.sql",
		"9ab82773b4be59130aab517604abf69c19e1c91ebae41ad69914724880ead9a6"
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
		"deba3f9aeecf5d4829477a1629bab8ce17095b802bdb34ccda0ad9d54f1c8d2b"
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
	ADD_SONG_DELETEDTIMESTAMP = (
		"014.add_song_deletedtimestamp.sql",
		"253a5504c86561a76083974f3a6332d2e7da2f15bbfc6c6019e2e6ea13da8c3b"
	)
	ADD_ALBUM_VERSION = (
		"015.add_album_version.sql",
		"aa6e370ebbe9243dffc2c609f5dd3385772b62275d2e24e8265bb7903781980e"
	)
	ADD_STATION_TYPE = (
		"016.add_station_type.sql",
		"72f7a6d41ab46e18c05d4649484d52a75c4ba66086b1ac44d8fc54962f7c10fc"
	)
	ADD_SONG_DELETEDBYUSERID = (
		"017.add_song_deletedbyuserid.sql",
		"e354453b26a884eeded27d0408a9682d8beca3a8a2b10974fd1235b3f14a13c2"
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
