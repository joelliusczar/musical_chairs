from musical_chairs_libs.services import (
	PlaylistService,
	PlaylistsUserService,
	AccountsService,
	UserRoleDef,
)
from musical_chairs_libs.dtos_and_utilities import (
	PlaylistCreationInfo,
	RulePriorityLevel
)
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_playlist_service as fixture_playlist_service,
	fixture_account_service as fixture_account_service,
	fixture_playlists_users_service as fixture_playlists_users_service,
)
from .common_fixtures import *
from .mocks.db_population import get_initial_playlists
from .mocks.db_data import bravo_user_id, juliet_user_id


def test_get_playlists_list(fixture_playlist_service: PlaylistService):
	playlistService = fixture_playlist_service
	data = list(playlistService.get_playlists())
	assert len(data) == 12

def test_get_playlists_list_with_admin(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService
	):
	playlistService = fixture_playlist_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == len(get_initial_playlists())
	data = sorted(
		playlistService.get_playlists(user=user, playlistKeys=16),
		key=lambda s:s.id
	)
	assert len(data) == 1
	assert data[0].viewsecuritylevel == RulePriorityLevel.LOCKED.value

def test_get_playlists_list_with_user_and_owner(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService
	):
	playlistService = fixture_playlist_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_bravo")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user, ownerId=user.id),
		key=lambda s:s.id
	)
	assert len(data) == 10
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	# assert data[10].name == "zulu_playlists"
	# assert data[11].name == "bravo_playlist_rerun"
	assert len(data[0].rules) == 7
	assert len(data[1].rules) == 7
	assert len(data[2].rules) == 7
	assert len(data[3].rules) == 7
	assert len(data[4].rules) == 7
	assert len(data[5].rules) == 7
	assert len(data[6].rules) == 7
	assert len(data[7].rules) == 7
	assert len(data[8].rules) == 7
	assert len(data[9].rules) == 7
	# assert len(data[10].rules) == 0
	# assert len(data[11].rules) == 0

	user,_ = accountService.get_account_for_login("testUser_juliet")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user, ownerId=user.id),
		key=lambda s:s.id
	)
	assert len(data) == 1
	assert data[0].name == "zulu_playlist"

	assert len(data[0].rules) == 7

def test_get_playlists_list_with_owner_and_scopes(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService
	):
	playlistService = fixture_playlist_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("ingo")
	assert user
	result = next(playlistService.get_playlists(
			17,
			user=user,
			scopes=[UserRoleDef.PLAYLIST_ASSIGN.value]
		), None)
	assert result

def test_save_playlist(
	fixture_playlist_service: PlaylistService,
	fixture_primary_user: AccountInfo
	):
	playlistService = fixture_playlist_service
	testData = PlaylistCreationInfo(
		name = "brand_new_playlists",
		description="Brand new playlist"
	)
	julietUser = AccountInfo(
		id = juliet_user_id,
		username="testUser_juliet",
		email="test10@munchopuncho.com"
	)
	result = playlistService.save_playlist(testData, julietUser)
	assert result and result.id == len(get_initial_playlists()) + 1
	fetched = next(playlistService.get_playlists(result.id))
	assert fetched.id == result.id
	assert fetched.name == "brand_new_playlists"
	assert fetched.description == "Brand new playlist"

	testData = PlaylistCreationInfo(
		name = "brand_new_playlist_fake_tag",
		description="Brand new playlist with bad tag"
	)
	result = playlistService.save_playlist(testData, julietUser)
	assert result and result.id == len(get_initial_playlists()) + 2
	fetched = next(playlistService.get_playlists(result.id))


	testData = PlaylistCreationInfo(
		name = "papa_playlist_update",
		description="Come to papa test"
	)
	bravoUser = AccountInfo(
		id = bravo_user_id,
		username="testUser_bravo",
		email="test2@munchopuncho.com"
	)
	result = playlistService.save_playlist(testData, bravoUser, 2)
	assert result and result.id == 2
	fetched = next(playlistService.get_playlists(result.id))
	assert fetched and fetched.name == "papa_playlist_update"
	assert fetched and fetched.description == "Come to papa test"


	testData = PlaylistCreationInfo(
		name = "oscar_playlists",
		description="Oscar the grouch"
	)
	result = playlistService.save_playlist(testData, fixture_primary_user, 1)
	assert result and result.id == 1
	fetched = next(playlistService.get_playlists(result.id))
	assert fetched and fetched.name == "oscar_playlists"
	assert fetched and fetched.description == "Oscar the grouch"

def test_get_playlists_with_view_security(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService
):
	playlistService = fixture_playlist_service
	accountService = fixture_account_service

	#no user
	data = sorted(
		playlistService.get_playlists(),
		key=lambda s:s.id
	)
	assert len(data) == 12
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	assert data[10].name == "zulu_playlist"
	assert data[11].name == "album_public_playlist_alpha"

	#user no roles
	user,_ = accountService.get_account_for_login("testUser_romeo")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	assert data[10].name == "zulu_playlist"
	assert data[11].name == "bravo_playlist_rerun"
	assert data[12].name == "album_public_playlist_alpha"

	#user with a site rule
	user,_ = accountService.get_account_for_login("testUser_whiskey")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 14
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	assert data[10].name == "zulu_playlist"
	assert data[11].name == "alpha_playlist_rerun"
	assert data[12].name == "bravo_playlist_rerun"
	assert data[13].name == "album_public_playlist_alpha"

	#user invited to see a playlist
	user,_ = accountService.get_account_for_login("testUser_xray")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 14
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	assert data[10].name == "zulu_playlist"
	assert data[11].name == "bravo_playlist_rerun"
	assert data[12].name == "charlie_playlist_rerun"
	assert data[13].name == "album_public_playlist_alpha"

	#owner a playlist
	user,_ = accountService.get_account_for_login("testUser_yankee")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 14
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	assert data[10].name == "zulu_playlist"
	assert data[11].name == "bravo_playlist_rerun"
	assert data[12].name == "delta_playlist_rerun"
	assert data[13].name == "album_public_playlist_alpha"
	pass

	user,_ = accountService.get_account_for_login("testUser_juliet")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 14

def test_get_playlists_with_scopes(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService
):
	playlistService = fixture_playlist_service
	accountService = fixture_account_service

	#no user
	data = sorted(
		playlistService.get_playlists(
			scopes=[UserRoleDef.PLAYLIST_ASSIGN.value]
		),
		key=lambda s:s.id
	)
	assert len(data) == 0

	#user no roles
	user,_ = accountService.get_account_for_login("testUser_romeo")
	assert user
	data = sorted(
		playlistService.get_playlists(
			user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13

	data = sorted(
		playlistService.get_playlists(
			user=user,
			scopes=[UserRoleDef.PLAYLIST_ASSIGN.value]
		),
		key=lambda s:s.id
	)
	assert len(data) == 0

	user,_ = accountService.get_account_for_login("testUser_india")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 14

	data = sorted(
		playlistService.get_playlists(
			user=user,
			scopes=[UserRoleDef.PLAYLIST_ASSIGN.value]
		),
		key=lambda s:s.id
	)
	assert len(data) == 14
	assert data[0].name == "oscar_playlist"
	assert data[1].name == "papa_playlist"
	assert data[2].name == "romeo_playlist"
	assert data[3].name == "sierra_playlist"
	assert data[4].name == "tango_playlist"
	assert data[5].name == "yankee_playlist"
	assert data[6].name == "uniform_playlist"
	assert data[7].name == "victor_playlist"
	assert data[8].name == "whiskey_playlist"
	assert data[9].name == "xray_playlist"
	assert data[10].name == "zulu_playlist"
	assert data[11].name == "alpha_playlist_rerun"
	assert data[12].name == "bravo_playlist_rerun"
	for playlist in data:
		assert len(playlist.rules) == 1

	user,_ = accountService.get_account_for_login("testUser_hotel")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13

	data = sorted(
		playlistService.get_playlists(
			user=user,
			scopes=[UserRoleDef.PLAYLIST_ASSIGN.value]
		),
		key=lambda s:s.id
	)

	assert len(data) == 1
	assert len(data[0].rules) == 1

def test_get_playlists_with_odd_priority(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService
):
	playlistService = fixture_playlist_service
	accountService = fixture_account_service

	user,_ = accountService.get_account_for_login("testUser_zulu")
	assert user
	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13

	user,_ = accountService.get_account_for_login("testUser_alice")
	assert user

	data = sorted(
		playlistService.get_playlists(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13

def test_get_playlist_user_list(
	fixture_playlist_service: PlaylistService,
	fixture_account_service: AccountsService,
	fixture_playlists_users_service: PlaylistsUserService
):
	playlistService = fixture_playlist_service
	playlistsUserService = fixture_playlists_users_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("ingo")
	assert user

	playlist = next(playlistService.get_playlists(17, user=user))
	result = sorted(
		playlistsUserService.get_playlist_users(playlist),
		key=lambda u: u.id
	)
	assert len(result) == 4

	assert result[0].username == "george"
	assert len(result[0].roles) == 1
	rules = sorted(result[0].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_VIEW.value

	assert result[1].username == "horsetel"
	assert len(result[1].roles) == 1
	rules = sorted(result[1].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_VIEW.value

	assert result[2].username == "ingo"
	assert len(result[2].roles) == 6
	rules = sorted(result[2].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_ASSIGN.value
	assert rules[1].name == UserRoleDef.PLAYLIST_DELETE.value
	assert rules[2].name == UserRoleDef.PLAYLIST_EDIT.value
	assert rules[3].name == UserRoleDef.PLAYLIST_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.PLAYLIST_USER_LIST.value
	assert rules[5].name == UserRoleDef.PLAYLIST_VIEW.value

	assert result[3].username == "narlon"
	assert len(result[3].roles) == 2
	rules = sorted(result[3].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_ASSIGN.value
	assert rules[1].name == UserRoleDef.PLAYLIST_VIEW.value

	playlist = next(playlistService.get_playlists(18, user=user))
	result = sorted(
		playlistsUserService.get_playlist_users(playlist),
		key=lambda u: u.id
	)
	assert len(result) == 2
	assert result[0].username == "ingo"
	assert len(result[0].roles) == 6
	rules = sorted(result[0].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_ASSIGN.value
	assert rules[1].name == UserRoleDef.PLAYLIST_DELETE.value
	assert rules[2].name == UserRoleDef.PLAYLIST_EDIT.value
	assert rules[3].name == UserRoleDef.PLAYLIST_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.PLAYLIST_USER_LIST.value
	assert rules[5].name == UserRoleDef.PLAYLIST_VIEW.value

	assert result[1].username == "narlon"
	assert len(result[1].roles) == 1
	rules = sorted(result[1].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_VIEW.value

	user,_ = accountService.get_account_for_login("testUser_victor")
	playlist = next(playlistService.get_playlists(12, user=user))
	result = sorted(
		playlistsUserService.get_playlist_users(playlist),
		key=lambda u: u.id
	)
	assert len(result) == 1
	assert result[0].username == "testUser_victor"
	assert len(result[0].roles) == 6
	rules = sorted(result[0].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_ASSIGN.value
	assert rules[1].name == UserRoleDef.PLAYLIST_DELETE.value
	assert rules[2].name == UserRoleDef.PLAYLIST_EDIT.value
	assert rules[3].name == UserRoleDef.PLAYLIST_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.PLAYLIST_USER_LIST.value
	assert rules[5].name == UserRoleDef.PLAYLIST_VIEW.value

def test_get_playlist_user_list_playlist_no_users(
	fixture_playlist_service: PlaylistService,
	fixture_playlists_users_service: PlaylistsUserService,
	fixture_account_service: AccountsService
):
	playlistService = fixture_playlist_service
	playlistsUserService = fixture_playlists_users_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("unruledStation_testUser")
	assert user

	playlist = next(playlistService.get_playlists(20, user=user))
	result = sorted(
		playlistsUserService.get_playlist_users(playlist),
		key=lambda u: u.id
	)
	assert len(result) == 1
	rules = sorted(result[0].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.PLAYLIST_ASSIGN.value
	assert rules[1].name == UserRoleDef.PLAYLIST_DELETE.value
	assert rules[2].name == UserRoleDef.PLAYLIST_EDIT.value
	assert rules[3].name == UserRoleDef.PLAYLIST_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.PLAYLIST_USER_LIST.value
	assert rules[5].name == UserRoleDef.PLAYLIST_VIEW.value

