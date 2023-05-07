import pytest
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SavedNameString,
	SearchNameString,
	UserRoleDef,
	ValidatedSongAboutInfo,
	AlbumInfo,
	ActionRule,
	PathsActionRule
)


def test_len_on_name_strings():
	savedName = SavedNameString("Hello")
	assert len(savedName) == 5
	searchName = SearchNameString("Hello")
	assert len(searchName) == 5

def test_name_strings_as_bool():
	savedName = SavedNameString("Hello")
	print("\ntesting cleaned strings")
	print(savedName)
	if savedName:
		assert True
	else:
		assert False
	savedNameEmpty = SavedNameString("")
	if savedNameEmpty:
		assert False
	else:
		assert True
	savedNameNull = SavedNameString(None)
	if savedNameNull:
		assert False
	else:
		assert True
	searchName = SearchNameString("Hello")
	if searchName:
		assert True
	else:
		assert False
	searchNameEmpty = SearchNameString("")
	if searchNameEmpty:
		assert False
	else:
		assert True
	searchNameNull = SearchNameString(None)
	if searchNameNull:
		assert False
	else:
		assert True

def test_is_admin():
	accountInfo = AccountInfo(
		id=-1,
		username="",
		email="",
		roles=[ActionRule(UserRoleDef.SONG_EDIT.value)]
	)
	assert not accountInfo.isAdmin
	accountInfo.roles.append(ActionRule(UserRoleDef.ADMIN.value))
	assert accountInfo.isAdmin

def test_validatedSongAboutInfo():
	songInfo = ValidatedSongAboutInfo()
	assert songInfo
	songInfo = ValidatedSongAboutInfo("Test")
	assert songInfo
	songInfo = ValidatedSongAboutInfo("Test", None)
	assert songInfo
	with pytest.raises(TypeError):
		songInfo = ValidatedSongAboutInfo("Test", AlbumInfo()) #pyright: ignore [reportGeneralTypeIssues]


def test_action_rule_ordering():

	r1 = ActionRule("alpha", priority=3)
	r2 = ActionRule("alpha", priority=3)

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 < r1)
	assert not (r2 > r1)
	assert (r2 <= r1)
	assert (r2 >= r1)

	r1 = ActionRule("alpha", priority=3)
	r2 = ActionRule("alpha", priority=4)

	assert not (r1 > r2)
	assert (r1 < r2)
	assert not (r1 >= r2)
	assert (r1 <= r2)

	assert (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert not (r2 <= r1)

	r1 = ActionRule("alpha", priority=3)
	r2 = ActionRule("alpha", priority=3, span=10)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("alpha", priority=3, span=10, count=5)
	r2 = ActionRule("alpha", priority=3, span=10, count=8)

	assert not (r1 > r2)
	assert (r1 < r2)
	assert not (r1 >= r2)
	assert (r1 <= r2)

	assert (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert not (r2 <= r1)

	r1 = ActionRule("alpha", priority=3, span=10, count=5)
	r2 = ActionRule("alpha", priority=3, span=10, count=5)

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("bravo", priority=3, span=10, count=5)
	r2 = ActionRule("alpha", priority=3, span=10, count=5)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("bravo", priority=3, span=10, count=5)
	r2 = ActionRule("alpha", priority=3, span=10, count=5)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("bravo", priority=3, span=10, count=5)
	r2 = ActionRule("alpha", priority=3, span=10, count=8)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("bravo", priority=3, span=10)
	r2 = ActionRule("alpha", priority=3, count=8)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("bravo", priority=3)
	r2 = ActionRule("alpha", priority=4)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)



def test_path_action_rule_ordering_no_path():

	r1 = PathsActionRule("alpha", priority=3)
	r2 = PathsActionRule("alpha", priority=3)

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3)
	r2 = PathsActionRule("alpha", priority=4)

	assert not (r1 > r2)
	assert (r1 < r2)
	assert not (r1 >= r2)
	assert (r1 <= r2)

	assert (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert not (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3)
	r2 = PathsActionRule("alpha", priority=3, span=10)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, span=10, count=5)
	r2 = PathsActionRule("alpha", priority=3, span=10, count=8)

	assert not (r1 > r2)
	assert (r1 < r2)
	assert not (r1 >= r2)
	assert (r1 <= r2)

	assert (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert not (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, span=10, count=5)
	r2 = PathsActionRule("alpha", priority=3, span=10, count=5)

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("bravo", priority=3, span=10, count=5)
	r2 = PathsActionRule("alpha", priority=3, span=10, count=5)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("bravo", priority=3, span=10, count=5)
	r2 = PathsActionRule("alpha", priority=3, span=10, count=5)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("bravo", priority=3, span=10, count=5)
	r2 = PathsActionRule("alpha", priority=3, span=10, count=8)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("bravo", priority=3, span=10)
	r2 = PathsActionRule("alpha", priority=3, count=8)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("bravo", priority=3)
	r2 = PathsActionRule("alpha", priority=4)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

def test_path_action_rule_ordering_with_path():

	r1 = PathsActionRule("alpha", priority=3)
	r2 = PathsActionRule("alpha", priority=3, path="a")

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, path="b")
	r2 = PathsActionRule("alpha", priority=3, path="a")

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, path="a")
	r2 = PathsActionRule("alpha", priority=3, path="a")

	assert not (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert (r1 <= r2)

	assert not (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, path="ab")
	r2 = PathsActionRule("alpha", priority=3, path="a")

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, path="ab")
	r2 = PathsActionRule("alpha", priority=4, path="a")

	assert not (r1 > r2)
	assert (r1 < r2)
	assert not (r1 >= r2)
	assert (r1 <= r2)

	assert (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert not (r2 <= r1)

	r1 = PathsActionRule("alpha", priority=3, path="ab")
	r2 = PathsActionRule("alpha", priority=3, path="a", span=10)

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)