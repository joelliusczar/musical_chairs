####### This file is generated. #######
# edit regen_file_reference_file #
# in mc_dev_ops.sh and rerun
from enum import Enum

class SqlScripts(Enum):
	GRANT_API = (
		"001.grant_api.sql",
		"77321d41fb61e0ca4197c05bfe2129df4a59567d5dd1749615d329b94498bf13"
	)
	GRANT_RADIO = (
		"002.grant_radio.sql",
		"5b27ee6d145c7b1054a8a94105b4a4a7b47aff1df60cf6e205ff810462bd098f"
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
		"4c12581aea1a6454c5cf85ceb266a41869144c0060ee7ecfc09ad04808526b48"
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
		"981fc1b8d3edd2adb3c26fa6f0e2c420f5ce9b1d0995748e0877b39bcd99e257"
	)
	ADD_SONG_DELETEDBYUSERID = (
		"017.add_song_deletedbyuserid.sql",
		"e354453b26a884eeded27d0408a9682d8beca3a8a2b10974fd1235b3f14a13c2"
	)
	ADD_SONG_TRACKNUM = (
		"018.add_song_tracknum.sql",
		"06424fe484636e17fca472b9a238a4af01af9919edfef22a524eb4f0853c9053"
	)
	ADD_PLAYLIST_VIEWSECURITY = (
		"019.add_playlist_viewsecurity.sql",
		"8b148e07872691319f43cda47d54cf0c1647f274d0b6009bc09d334384990de0"
	)
	RENAME_PLAYLIST_SONG_TABLE = (
		"021.rename_playlist_song_table.sql",
		"0b784690f066ee79517b5c661b3745796d1899c1899c970eb5fe855bf0a7a84d"
	)
	ADD_STATION_BITRATE = (
		"022.add_station_bitrate.sql",
		"2d822eeb7b370bf1d5d1c2748883b40cbb2146d64a13177bfc0c81dd55dd2de7"
	)
	ADD_PLAYLISTSSONGS_ORDER = (
		"023.add_playlistssongs_order.sql",
		"0cf0a767eea4a75bd8d45c7f5b622bafb0a9942c7e6246737589f845f255ac8a"
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
