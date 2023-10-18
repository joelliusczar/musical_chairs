from musical_chairs_libs.services import (
	SongFileService,
	PathRuleService
)
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_song_file_service as fixture_song_file_service,
	fixture_path_rule_service as fixture_path_rule_service
)
from .common_fixtures import *
from io import BytesIO



def test_song_ls(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha") #random user
	assert user
	paths = sorted(songFileService.song_ls(user), key=lambda d: d.path)
	assert len(paths) == 4
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

	paths = sorted(songFileService.song_ls(user, "foo/"), key=lambda d: d.path)
	assert len(paths) == 4
	assert paths[0].path == "foo/bar/"
	assert paths[1].path == "foo/dude/"
	assert paths[2].path == "foo/goo/"
	assert paths[3].path == "foo/rude/"

def test_add_directory(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	songFileService.create_directory("foo", "create_dir_test", user.id)
	paths = sorted(songFileService.song_ls(user, "foo/"), key=lambda d: d.path)
	assert len(paths) == 5
	assert paths[0].path == "foo/bar/"
	assert paths[1].path == "foo/create_dir_test/"
	assert paths[2].path == "foo/dude/"
	assert paths[3].path == "foo/goo/"
	assert paths[4].path == "foo/rude/"

	paths = sorted(
		songFileService.song_ls(user, "foo/create_dir_test"),
		key=lambda d: d.path
	)
	assert len(paths) == 1

	paths = sorted(
		songFileService.song_ls(user, "foo/create_dir_test/"),
		key=lambda d: d.path
	)
	assert len(paths) == 1

def test_add_directory_to_leaves(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	songFileService.create_directory(
		"foo/goo/boo",
		"create_dir_test",
		user.id
	)
	paths = sorted(
		songFileService.song_ls(user, "foo/goo/boo/"),
		key=lambda d: d.path
	)
	assert len(paths) == 6
	assert paths[0].path == "foo/goo/boo/create_dir_test/"
	assert paths[1].path == "foo/goo/boo/sierra"
	assert paths[2].path == "foo/goo/boo/tango"
	assert paths[3].path == "foo/goo/boo/uniform"
	assert paths[4].path == "foo/goo/boo/victor"
	assert paths[5].path == "foo/goo/boo/victor_2"
	songFileService.save_song_file(
		BytesIO(b"abc"),
		"foo/goo/boo/create_dir_test",
		"create_test_song",
		user.id
	)
	paths = sorted(
		songFileService.song_ls(user, "foo/goo/boo/"),
		key=lambda d: d.path
	)
	assert paths[0].totalChildCount == 1
	paths = sorted(
		songFileService.song_ls(user, "foo/goo/boo/create_dir_test/"),
		key=lambda d: d.path
	)
	assert len(paths) == 1

def test_song_ls_user_with_paths(
	fixture_song_file_service: SongFileService,
	fixture_path_user_factory: Callable[[str], AccountInfo]
):
	songFileService = fixture_song_file_service
	user = fixture_path_user_factory("testUser_uniform") #random user
	paths = sorted(songFileService.song_ls(user),key=lambda d: d.path)
	# this is no longer expected behavior
	# assert len(paths) == 2
	# assert paths[0].path == "foo/bar/"
	# assert paths[1].path == "foo/dude/"

	assert len(paths) == 1
	assert paths[0].path == "foo/"

	paths = sorted(songFileService.song_ls(user, "foo/"), key=lambda d: d.path)
	assert len(paths) == 2
	assert paths[0].path == "foo/bar/"
	assert paths[1].path == "foo/dude/"

def test_get_user_paths(
	fixture_path_rule_service: PathRuleService
):
	pathRuleService = fixture_path_rule_service
	results = list(pathRuleService.get_paths_user_can_see(11))
	assert results

def test_get_parents_of_path(
	fixture_song_file_service: SongFileService
):
	songFileService = fixture_song_file_service
	results = sorted(
		songFileService.get_parents_of_path("foo"),
		key=lambda r: r[1]
	)
	assert not results
	results = sorted(
		songFileService.get_parents_of_path("/foo"),
		key=lambda r: r[1]
	)
	assert not results

	results = sorted(
		songFileService.get_parents_of_path("foo/goo/boo/sierra/rapture"),
		key=lambda r: r[1]
	)
	assert len(results) == 1

	results = sorted(
		songFileService.get_parents_of_path("foo/goo/boo/sierra"),
		key=lambda r: r[1]
	)
	assert len(results) == 1