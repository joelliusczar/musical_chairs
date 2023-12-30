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
	user,_ = accountService.get_account_for_login("testUser_alpha")
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

	paths = sorted(songFileService.song_ls(user, "tossedSlash/trap/"),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == "tossedSlash/trap/bang(pow)_1/"

	paths = sorted(songFileService.song_ls(user, "tossedSlash/trap/bang(pow)_1/"),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == "tossedSlash/trap/bang(pow)_1/boo"

def test_song_ls_overlaping_paths(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	paths = sorted(
		songFileService.song_ls(user, "jazz/"),
		key=lambda d: d.path
	)
	assert len(paths) == 6
	assert paths[0].path == "jazz/cat/"
	assert paths[1].path == "jazz/lurk/"
	assert paths[2].path == "jazz/overlap/"
	assert paths[3].path == "jazz/overlaper/"
	assert paths[4].path == "jazz/overloop/"
	assert paths[5].path == "jazz/rude/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/o"),
		key=lambda d: d.path
	)
	assert len(paths) == 3
	assert paths[0].path == "jazz/overlap/"
	assert paths[1].path == "jazz/overlaper/"
	assert paths[2].path == "jazz/overloop/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/overl"),
		key=lambda d: d.path
	)
	assert len(paths) == 3
	assert paths[0].path == "jazz/overlap/"
	assert paths[1].path == "jazz/overlaper/"
	assert paths[2].path == "jazz/overloop/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/overla"),
		key=lambda d: d.path
	)
	assert len(paths) == 2
	assert paths[0].path == "jazz/overlap/"
	assert paths[1].path == "jazz/overlaper/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/overlap"),
		key=lambda d: d.path
	)
	assert len(paths) == 2
	assert paths[0].path == "jazz/overlap/"
	assert paths[1].path == "jazz/overlaper/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/overlap/"),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == "jazz/overlap/toon/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/overlaper"),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == "jazz/overlaper/"

	paths = sorted(
		songFileService.song_ls(user, "jazz/overlaper/"),
		key=lambda d: d.path
	)
	assert len(paths) == 2
	assert paths[0].path == "jazz/overlaper/soon/"
	assert paths[1].path == "jazz/overlaper/toon/"

def test_song_ls_paths_with_spaces(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	paths = sorted(
		songFileService.song_ls(user, "blitz/"),
		key=lambda d: d.path
	)
	assert len(paths) == 4
	assert paths[0].path == "blitz/  are we handling/"
	assert paths[1].path == "blitz/how well are we handing/"
	assert paths[2].path == "blitz/mar/"
	assert paths[3].path == "blitz/rhino/"

	paths = sorted(
		songFileService.song_ls(user, "blitz/ "),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == "blitz/  are we handling/"

	paths = sorted(
		songFileService.song_ls(user, "blitz/  are we handling"),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == "blitz/  are we handling/"

	paths = sorted(
		songFileService.song_ls(user, "blitz/  are we handling/"),
		key=lambda d: d.path
	)
	assert len(paths) == 1
	assert paths[0].path == \
		"blitz/  are we handling/ dirs beginning with space  /"
	
	paths = sorted(
		songFileService.song_ls(user, "blitz/   "),
		key=lambda d: d.path
	)
	assert len(paths) == 0

	paths = sorted(
		songFileService.song_ls(user, "blitz/  are we  "),
		key=lambda d: d.path
	)
	assert len(paths) == 0



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

def test_prefix_split_(
	fixture_song_file_service: SongFileService
):
	songFileService = fixture_song_file_service
	results = list(songFileService.__prefix_split__(""))
	assert len(results) == 1
	assert results[0] == "/"

	results = list(songFileService.__prefix_split__("/"))
	assert len(results) == 1
	assert results[0] == "/"

	results = list(songFileService.__prefix_split__("alpha"))
	assert len(results) == 2
	assert results[0] == "/"
	assert results[1] == "/alpha/"

	input = "alpha/bravo"
	results = list(songFileService.__prefix_split__(input))
	assert len(results) == 3
	assert results[0] == "/"
	assert results[1] == "/alpha/"
	assert results[2] == "/alpha/bravo/"

	input = "alpha/bravo/charlie"
	results = list(songFileService.__prefix_split__(input))
	assert len(results) == 4
	assert results[0] == "/"
	assert results[1] == "/alpha/"
	assert results[2] == "/alpha/bravo/"
	assert results[3] == "/alpha/bravo/charlie/"


def test_get_parent_directoriess_0(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	result = songFileService.get_parent_directoriess(user, "")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

def test_get_parent_directoriess_1(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "/")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

def test_get_parent_directoriess_2(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "/f")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 4
	paths= sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

def test_get_parent_directoriess_3(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "/foo/")
	assert len(result) == 2
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"
	
	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.path)
	assert fooPaths[0].path == "foo/bar/"
	assert fooPaths[1].path == "foo/dude/"
	assert fooPaths[2].path == "foo/goo/"
	assert fooPaths[3].path == "foo/rude/"

def test_get_parent_directoriess_4(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "/foo/rude/")
	assert len(result) == 3

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.path)
	assert fooPaths[0].path == "foo/bar/"
	assert fooPaths[1].path == "foo/dude/"
	assert fooPaths[2].path == "foo/goo/"
	assert fooPaths[3].path == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.path)
	assert fooRudePaths[0].path == "foo/rude/bog/"
	assert fooRudePaths[1].path == "foo/rude/rog/"

def test_get_parent_directoriess_5(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "foo/rude/bog")
	assert len(result) == 4

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.path)
	assert fooPaths[0].path == "foo/bar/"
	assert fooPaths[1].path == "foo/dude/"
	assert fooPaths[2].path == "foo/goo/"
	assert fooPaths[3].path == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.path)
	assert fooRudePaths[0].path == "foo/rude/bog/"
	assert fooRudePaths[1].path == "foo/rude/rog/"

	assert "foo/rude/bog/" in result
	assert len(result["foo/rude/bog/"]) == 2
	fooRudeBogPaths = sorted(result["foo/rude/bog/"], key=lambda d: d.path)
	assert fooRudeBogPaths[0].path == "foo/rude/bog/kilo2"
	assert fooRudeBogPaths[1].path == "foo/rude/bog/lima2"

def test_get_parent_directoriess_6(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "foo/rude/bog/kilo2")
	assert len(result) == 4

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.path)
	assert fooPaths[0].path == "foo/bar/"
	assert fooPaths[1].path == "foo/dude/"
	assert fooPaths[2].path == "foo/goo/"
	assert fooPaths[3].path == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.path)
	assert fooRudePaths[0].path == "foo/rude/bog/"
	assert fooRudePaths[1].path == "foo/rude/rog/"

	assert "foo/rude/bog/" in result
	assert len(result["foo/rude/bog/"]) == 2
	fooRudeBogPaths = sorted(result["foo/rude/bog/"], key=lambda d: d.path)
	assert fooRudeBogPaths[0].path == "foo/rude/bog/kilo2"
	assert fooRudeBogPaths[1].path == "foo/rude/bog/lima2"

def test_get_parent_directoriess_of_bad_path(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.get_parent_directoriess(user, "foo/rude/x/")
	assert len(result) == 3

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.path)
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.path)
	assert fooPaths[0].path == "foo/bar/"
	assert fooPaths[1].path == "foo/dude/"
	assert fooPaths[2].path == "foo/goo/"
	assert fooPaths[3].path == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.path)
	assert fooRudePaths[0].path == "foo/rude/bog/"
	assert fooRudePaths[1].path == "foo/rude/rog/"
