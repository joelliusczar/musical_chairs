from musical_chairs_libs.services import (
	SongFileService,
	PathRuleService,
	JobsService,
	QueueService,
)
from musical_chairs_libs.dtos_and_utilities import (
	DirectoryTransfer,
	QueueMetrics,
)
from musical_chairs_libs.dtos_and_utilities.constants import JobStatusTypes
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_song_file_service as fixture_song_file_service,
	fixture_path_rule_service as fixture_path_rule_service,
	fixture_job_service as fixture_job_service,
	fixture_queue_service as fixture_queue_service,
	fixture_station_service as fixture_station_service
)
from .common_fixtures import *
from io import BytesIO
from .mocks.db_data.user_ids import uniform_user_id


@pytest.mark.current_username("testUser_alpha")
def test_song_ls(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	paths = sorted(songFileService.song_ls(), key=lambda d: d.treepath)
	assert len(paths) == 4
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"

	paths = sorted(songFileService.song_ls("foo/"), key=lambda d: d.treepath)
	assert len(paths) == 4
	assert paths[0].treepath == "foo/bar/"
	assert paths[1].treepath == "foo/dude/"
	assert paths[2].treepath == "foo/goo/"
	assert paths[3].treepath == "foo/rude/"

	paths = sorted(songFileService.song_ls("tossedSlash/trap/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == "tossedSlash/trap/bang(pow)_1/"

	paths = sorted(songFileService.song_ls("tossedSlash/trap/bang(pow)_1/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == "tossedSlash/trap/bang(pow)_1/boo"

@pytest.mark.current_username("testUser_alpha")
def test_song_ls_overlaping_paths(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	paths = sorted(
		songFileService.song_ls("jazz/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 6
	assert paths[0].treepath == "jazz/cat/"
	assert paths[1].treepath == "jazz/lurk/"
	assert paths[2].treepath == "jazz/overlap/"
	assert paths[3].treepath == "jazz/overlaper/"
	assert paths[4].treepath == "jazz/overloop/"
	assert paths[5].treepath == "jazz/rude/"

	paths = sorted(
		songFileService.song_ls("jazz/o"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 3
	assert paths[0].treepath == "jazz/overlap/"
	assert paths[1].treepath == "jazz/overlaper/"
	assert paths[2].treepath == "jazz/overloop/"

	paths = sorted(
		songFileService.song_ls("jazz/overl"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 3
	assert paths[0].treepath == "jazz/overlap/"
	assert paths[1].treepath == "jazz/overlaper/"
	assert paths[2].treepath == "jazz/overloop/"

	paths = sorted(
		songFileService.song_ls("jazz/overla"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 2
	assert paths[0].treepath == "jazz/overlap/"
	assert paths[1].treepath == "jazz/overlaper/"

	paths = sorted(
		songFileService.song_ls("jazz/overlap"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 2
	assert paths[0].treepath == "jazz/overlap/"
	assert paths[1].treepath == "jazz/overlaper/"

	paths = sorted(
		songFileService.song_ls("jazz/overlap/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == "jazz/overlap/toon/"

	paths = sorted(
		songFileService.song_ls("jazz/overlaper"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == "jazz/overlaper/"

	paths = sorted(
		songFileService.song_ls("jazz/overlaper/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 2
	assert paths[0].treepath == "jazz/overlaper/soon/"
	assert paths[1].treepath == "jazz/overlaper/toon/"


@pytest.mark.current_username("testUser_alpha")
def test_song_ls_paths_with_spaces(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	paths = sorted(
		songFileService.song_ls("blitz/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 4
	assert paths[0].treepath == "blitz/  are we handling/"
	assert paths[1].treepath == "blitz/how well are we handling/"
	assert paths[2].treepath == "blitz/mar/"
	assert paths[3].treepath == "blitz/rhino/"

	paths = sorted(
		songFileService.song_ls("blitz/ "),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == "blitz/  are we handling/"

	paths = sorted(
		songFileService.song_ls("blitz/  are we handling"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == "blitz/  are we handling/"

	paths = sorted(
		songFileService.song_ls("blitz/  are we handling/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	assert paths[0].treepath == \
		"blitz/  are we handling/ dirs beginning with space  /"
	
	paths = sorted(
		songFileService.song_ls("blitz/   "),
		key=lambda d: d.treepath
	)
	assert len(paths) == 0

	paths = sorted(
		songFileService.song_ls("blitz/  are we  "),
		key=lambda d: d.treepath
	)
	assert len(paths) == 0


@pytest.mark.current_username("testUser_alpha")
def test_add_directory(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	songFileService.create_directory("foo", "create_dir_test")
	paths = sorted(songFileService.song_ls("foo/"), key=lambda d: d.treepath)
	assert len(paths) == 5
	assert paths[0].treepath == "foo/bar/"
	assert paths[1].treepath == "foo/create_dir_test/"
	assert paths[2].treepath == "foo/dude/"
	assert paths[3].treepath == "foo/goo/"
	assert paths[4].treepath == "foo/rude/"

	paths = sorted(
		songFileService.song_ls("foo/create_dir_test"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1

	paths = sorted(
		songFileService.song_ls("foo/create_dir_test/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1

@pytest.mark.current_username("testUser_alpha")
def test_add_unicode_directory(
	fixture_song_file_service: SongFileService,
):
	songFileService = fixture_song_file_service
	songFileService.create_directory("foo", "ü")
	paths = sorted(songFileService.song_ls("foo/"), key=lambda d: d.treepath)
	assert len(paths) == 5
	assert paths[0].treepath == "foo/bar/"
	assert paths[1].treepath == "foo/dude/"
	assert paths[2].treepath == "foo/goo/"
	assert paths[3].treepath == "foo/rude/"
	assert paths[4].treepath == "foo/ü/"

	songFileService.create_directory("foo/ü", "u")
	paths = sorted(songFileService.song_ls("foo/ü/"), key=lambda d: d.treepath)
	assert len(paths) == 1
	assert paths[0].treepath == "foo/ü/u/"


@pytest.mark.current_username("testUser_kilo")
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
		"create_dir_test"
	)
	paths = sorted(
		songFileService.song_ls("foo/goo/boo/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 6
	assert paths[0].treepath == "foo/goo/boo/create_dir_test/"
	assert paths[1].treepath == "foo/goo/boo/sierra"
	assert paths[2].treepath == "foo/goo/boo/tango"
	assert paths[3].treepath == "foo/goo/boo/uniform"
	assert paths[4].treepath == "foo/goo/boo/victor"
	assert paths[5].treepath == "foo/goo/boo/victor_2"
	songFileService.save_song_file(
		BytesIO(b"abc"),
		"foo/goo/boo/create_dir_test",
		"create_test_song"
	)
	paths = sorted(
		songFileService.song_ls("foo/goo/boo/"),
		key=lambda d: d.treepath
	)
	assert paths[0].totalChildCount == 1
	paths = sorted(
		songFileService.song_ls("foo/goo/boo/create_dir_test/"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1

@pytest.mark.current_username("testUser_uniform")
def test_song_ls_user_with_paths(
	fixture_song_file_service: SongFileService,
):
	songFileService = fixture_song_file_service
	paths = sorted(songFileService.song_ls(),key=lambda d: d.treepath)
	# this is no longer expected behavior
	# assert len(paths) == 2
	# assert paths[0].path == "foo/bar/"
	# assert paths[1].path == "foo/dude/"

	assert len(paths) == 1
	assert paths[0].treepath == "foo/"

	paths = sorted(songFileService.song_ls("foo/"), key=lambda d: d.treepath)
	assert len(paths) == 2
	assert paths[0].treepath == "foo/bar/"
	assert paths[1].treepath == "foo/dude/"

@pytest.mark.current_username("testUser_uniform")
def test_get_user_paths(
	fixture_path_rule_service: PathRuleService
):
	pathRuleService = fixture_path_rule_service
	results = list(pathRuleService.get_paths_user_can_see(uniform_user_id))
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

@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directories_empty_str_admin(
	fixture_song_file_service: SongFileService,
):
	songFileService = fixture_song_file_service

	result = songFileService.song_ls_parents("")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"

@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directories_empty_str(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	result = songFileService.song_ls_parents("")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directories_single_slash_admin(
	fixture_song_file_service: SongFileService,
):
	songFileService = fixture_song_file_service

	result = songFileService.song_ls_parents("/")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"


@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_single_slash(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("/")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directories_partial_segment_admin(
	fixture_song_file_service: SongFileService,
):
	songFileService = fixture_song_file_service

	result = songFileService.song_ls_parents("/f")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"


@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_partial_segment(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("/f")
	assert len(result) == 1
	assert "/" in result
	assert len(result["/"]) == 1
	paths= sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"


@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_first_segment(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("/foo/")
	assert len(result) == 2
	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"
	
	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directoriess_first_segment_admin(
	fixture_song_file_service: SongFileService
):
	songFileService = fixture_song_file_service

	result = songFileService.song_ls_parents("/foo/")
	assert len(result) == 2
	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"
	
	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"


@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_2_segments(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("/foo/rude/")
	assert len(result) == 3

	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directoriess_2_segments_admin(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("/foo/rude/")
	assert len(result) == 3

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"

@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_3_segments(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("foo/rude/bog")
	assert len(result) == 4

	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"

	assert "foo/rude/bog/" in result
	assert len(result["foo/rude/bog/"]) == 2
	fooRudeBogPaths = sorted(result["foo/rude/bog/"], key=lambda d: d.treepath)
	assert fooRudeBogPaths[0].treepath == "foo/rude/bog/kilo2"
	assert fooRudeBogPaths[1].treepath == "foo/rude/bog/lima2"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directoriess_3_segments_admin(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("foo/rude/bog")
	assert len(result) == 4

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"

	assert "foo/rude/bog/" in result
	assert len(result["foo/rude/bog/"]) == 2
	fooRudeBogPaths = sorted(result["foo/rude/bog/"], key=lambda d: d.treepath)
	assert fooRudeBogPaths[0].treepath == "foo/rude/bog/kilo2"
	assert fooRudeBogPaths[1].treepath == "foo/rude/bog/lima2"


@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_4_segments(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("foo/rude/bog/kilo2")
	assert len(result) == 4

	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"

	assert "foo/rude/bog/" in result
	assert len(result["foo/rude/bog/"]) == 2
	fooRudeBogPaths = sorted(result["foo/rude/bog/"], key=lambda d: d.treepath)
	assert fooRudeBogPaths[0].treepath == "foo/rude/bog/kilo2"
	assert fooRudeBogPaths[1].treepath == "foo/rude/bog/lima2"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directoriess_4_segments_admin(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("foo/rude/bog/kilo2")
	assert len(result) == 4

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"

	assert "foo/rude/bog/" in result
	assert len(result["foo/rude/bog/"]) == 2
	fooRudeBogPaths = sorted(result["foo/rude/bog/"], key=lambda d: d.treepath)
	assert fooRudeBogPaths[0].treepath == "foo/rude/bog/kilo2"
	assert fooRudeBogPaths[1].treepath == "foo/rude/bog/lima2"


@pytest.mark.current_username("testUser_kilo")
def test_get_parent_directoriess_of_bad_path(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("foo/rude/x/")
	assert len(result) == 3

	assert "/" in result
	assert len(result["/"]) == 1
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "foo/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"


@pytest.mark.current_username("testUser_alpha")
def test_get_parent_directoriess_of_bad_path_admin(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user

	result = songFileService.song_ls_parents("foo/rude/x/")
	assert len(result) == 3

	assert "/" in result
	assert len(result["/"]) == 4
	paths = sorted(result["/"], key=lambda d: d.treepath)
	assert paths[0].treepath == "blitz/"
	assert paths[1].treepath == "foo/"
	assert paths[2].treepath == "jazz/"
	assert paths[3].treepath == "tossedSlash/"

	assert "foo/" in result
	assert len(result["foo/"]) == 4
	fooPaths = sorted(result["foo/"], key=lambda d: d.treepath)
	assert fooPaths[0].treepath == "foo/bar/"
	assert fooPaths[1].treepath == "foo/dude/"
	assert fooPaths[2].treepath == "foo/goo/"
	assert fooPaths[3].treepath == "foo/rude/"

	assert "foo/rude/" in result
	assert len(result["foo/rude/"]) == 2
	fooRudePaths = sorted(result["foo/rude/"], key=lambda d: d.treepath)
	assert fooRudePaths[0].treepath == "foo/rude/bog/"
	assert fooRudePaths[1].treepath == "foo/rude/rog/"


@pytest.mark.current_username("testUser_kilo")
def test_delete_directory(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	songFileService.create_directory("foo/goo", "testdir")
	result = songFileService.song_ls_parents("foo/goo")
	assert len(result["foo/goo/"]) == 12
	assert "foo/goo/testdir/" in (p.treepath for p in result["foo/goo/"])
	result = songFileService.delete_prefix("foo/goo/testdir/")
	assert len(result["foo/goo/"]) == 11
	assert "foo/goo/testdir/" not in (p.treepath for p in result["foo/goo/"])

@pytest.mark.current_username("testUser_kilo")
def test_delete_dir_with_songs(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService,
	fixture_job_service: JobsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	jobService = fixture_job_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	songFileService.delete_prefix("foo/goo/koo/")
	jobs = list(jobService.get_all())
	assert len(jobs) == 3
	jobService.process_deleted_songs()
	jobs = list(jobService.get_all())
	assert all(j.status == JobStatusTypes.COMPLETED.value for j in jobs)
	assert len(jobs) == 3


@pytest.mark.current_username("testUser_kilo")
def test_delete_song_in_station(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService,
	fixture_queue_service: QueueService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	queueService = fixture_queue_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	deletedSongId = 41
	stationId = 2

	station = queueService.__get_station__(stationId)
	queueService.fil_up_queue(station, QueueMetrics(maxSize=50))
	queue, _ = queueService.get_queue_for_station(stationId)
	catalogue, _ = queueService.get_catalogue(stationId)
	assert deletedSongId in (s.id for s in catalogue)
	assert deletedSongId in (s.id for s in queue)
	assert queueService.can_song_be_queued_to_station(deletedSongId, stationId)
	songFileService.soft_delete_songs([deletedSongId])

	queue2, _ = queueService.get_queue_for_station(stationId)
	#technically these should be not in but I figured, the queue is pretty
	#ephermeral anyway so we'll just let it be the last remnants
	assert deletedSongId in (s.id for s in queue2)
	catalogue2, _ = queueService.get_catalogue(stationId)
	assert deletedSongId not in (s.id for s in catalogue2)
	assert not queueService.can_song_be_queued_to_station(deletedSongId, stationId)

	
@pytest.mark.current_username("testUser_kilo")
def test_parent_ls_with_placeholder_dir(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	songFileService.create_directory("foo/goo", "testdir")
	result = songFileService.song_ls_parents("foo/goo/testdir/")
	pass
	assert len(result["foo/goo/"]) == 12
	assert sum(
		1 for n in result["foo/goo/"] if n.treepath.endswith("testdir/")
	) == 1


@pytest.mark.echo(False)
@pytest.mark.current_username("testUser_alpha")
def test_move_path(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #owns stuff
	assert user
	transfer = DirectoryTransfer(
		treepath="foo/rude/rog/mike2",
		newprefix="foo/rude/bog/"
	)
	srcInitial = list(songFileService.song_ls("foo/rude/rog/"))
	assert len(srcInitial) == 3
	result = songFileService.move_path(transfer)
	updatedDir = result["foo/rude/bog/"]
	assert len(updatedDir) == 3
	srcUpdated = list(songFileService.song_ls("foo/rude/rog/"))
	assert len(srcUpdated) == 2

	transfer = DirectoryTransfer(
		treepath="foo/bar/baz/",
		newprefix="foo/dude/"
	)
	result = songFileService.move_path(transfer)

	transfer = DirectoryTransfer(
		treepath="",
		newprefix="foo/dude/"
	)
	with pytest.raises(ValueError):
		songFileService.move_path(transfer)
	pass

@pytest.mark.current_username("testUser_alpha")
def test_song_ls_with_wild_cards(
	fixture_song_file_service: SongFileService,
	fixture_account_service: AccountsService
):
	songFileService = fixture_song_file_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	paths = sorted(
		songFileService.song_ls("foo/dude/alpha_"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1
	paths = sorted(
		songFileService.song_ls("foo/dude/al%"),
		key=lambda d: d.treepath
	)
	assert len(paths) == 1