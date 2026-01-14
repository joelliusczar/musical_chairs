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
		"0d48302f848ab80ccdcc12b947a493225ae0e068ce05568293bbdddbea66e495"
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
		"29e7bf5f38dbb9e64aeabbacdd8bf203655e67b4ac1276175f3371a7461f6432"
	)
	ADD_STATION_BITRATE = (
		"022.add_station_bitrate.sql",
		"2d822eeb7b370bf1d5d1c2748883b40cbb2146d64a13177bfc0c81dd55dd2de7"
	)
	ADD_PLAYLISTSSONGS_ORDER = (
		"023.add_playlistssongs_order.sql",
		"0cf0a767eea4a75bd8d45c7f5b622bafb0a9942c7e6246737589f845f255ac8a"
	)
	GRANT_API_PLAYLISTSSONGS = (
		"024.grant_api_playlistssongs.sql",
		"55c76cc6941b5584a38abb4199002ab4ff3544bc242ea9da66b065489d67f3e0"
	)
	GRANT_RADIO_PLAYLISTSSONGS = (
		"025.grant_radio_playlistssongs.sql",
		"e86d10cb8ac811f077fb5e8c97e164d18ed1605cf4e7d6d73c73046b80db57be"
	)
	DROP_PLAYLISTSSONGS_ORDER = (
		"026.drop_playlistssongs_order.sql",
		"e343fe40c42ffbc132e540e6f90ca5d2f95419107a083029bf6e54821bb2071d"
	)
	ADD_PLAYLISTSSONGS_LEXORDER = (
		"027.add_playlistssongs_lexorder.sql",
		"c3e575de46266f14741ecc3dfd90f69f580e52a0a90c5a1a0bdcd99cfe1bd122"
	)
	DROP_UNIQUE_ALBUM_INDEX = (
		"028.drop_unique_album_index.sql",
		"86cd90a037119ca3bd662d5a9e7ab90169279c8cd89056997ad5ae69c8b87eb3"
	)
	READD_UNIQUE_ALBUM_INDEX = (
		"029.readd_unique_album_index.sql",
		"677d9fb8447622a504e129a32d2885ecf2918df2f0735587ebbcc591cc681615"
	)
	ADD_STATIONQUEUE_ITEMTYPE = (
		"030.add_stationqueue_itemtype.sql",
		"277c2d0e9aef329749dbd1e7a01e24ffaceea1991056d38f13aa322dd692447b"
	)
	ADD_STATIONQUEUE_PARENTKEY = (
		"031.add_stationqueue_parentkey.sql",
		"df5413ff48388b37c4a50f95be9e13196260a4aa6aac0e70d8deb7bd476a7bd9"
	)
	ADD_LASTPLAYED_ITEMTYPE = (
		"032.add_lastplayed_itemtype.sql",
		"3ec4eeb8335242efcae8ebe2bcf2401d07a9f73338ec48cb27b157909a5d9e45"
	)
	ADD_LASTPLATED_PARENTKEY = (
		"033.add_lastplated_parentkey.sql",
		"91f3a777c1b93bf4db9cb24b9c0bd9141170fac4a76b696a9bd48b6acf25040f"
	)
	DROP_UNIQUE_LASTPLAYED_INDEX = (
		"034.drop_unique_lastplayed_index.sql",
		"8539b6995f65899bec1496c3aa99558f67d985d8807fbcf4dea673ac4d9845ac"
	)
	READD_UNIQUE_LASTPLAYED_INDEX = (
		"035.readd_unique_lastplayed_index.sql",
		"4d14ed810a4af9a51243bd0171654d529ca03fb69df7b6bba5bbc35b5813cb9e"
	)
	UPDATE_COLLATIONS = (
		"036.update_collations.sql",
		"ffda3d82c1a50ea25dab4d00ec79446f5390644ef7fda88af293e0bdd83a3852"
	)
	SONGS_EXPAND_GENRE = (
		"037.songs_expand_genre.sql",
		"053387198a342aabf0f3e157971096e56f9a12e33cfc31eff2a02574b83ff0b9"
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
