import pytest
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	SavedNameString,
	SearchNameString,
	UserRoleDef,
	ValidatedSongAboutInfo,
	AlbumInfo,
	ActionRule,
	PathsActionRule,
	StationActionRule,
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
	assert not accountInfo.isadmin
	accountInfo.roles.append(ActionRule(UserRoleDef.ADMIN.value))
	assert accountInfo.isadmin

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

	s = sorted([r1, r2])
	assert s[0] == r2

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

	s = sorted([r1, r2])
	assert s[0] == r2

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

	s = sorted([r1, r2])
	assert s[0] == r1

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

	s = sorted([r1, r2])
	assert s[0] == r2

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

	s = sorted([r1, r2])
	assert s[0] == r2

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

	s = sorted([r1, r2])
	assert s[0] == r2

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

	s = sorted([r1, r2])
	assert s[0] == r2

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

	s = sorted([r1, r2])
	assert s[0] == r2

	assert (r1 > r2)
	assert not (r1 < r2)
	assert (r1 >= r2)
	assert not (r1 <= r2)

	assert not (r2 > r1)
	assert (r2 < r1)
	assert not (r2 >= r1)
	assert (r2 <= r1)

	r1 = ActionRule("alpha", priority=1, span=300, count=15)
	r2 = ActionRule("alpha", priority=1, span=300, count=25)

	s = sorted([r1, r2])
	assert s[0] == r1

	assert not (r1 > r2)
	assert (r1 < r2)
	assert not (r1 >= r2)
	assert (r1 <= r2)

	assert (r2 > r1)
	assert not (r2 < r1)
	assert (r2 >= r1)
	assert not (r2 <= r1)

	r1 = ActionRule("alpha", priority=1)
	r2 = ActionRule("alpha", priority=1, span=300, count=15)
	r3 = ActionRule("alpha", priority=1, span=300, count=25)
	r4 = ActionRule("alpha", priority=2, span=300, count=25)
	r5 = ActionRule("alpha", priority=2)
	r6 = ActionRule("alpha", priority=2, span=300, count=15)
	r7 = ActionRule("bravo", priority=1, span=300, count=15)
	r8 = ActionRule("bravo", priority=1, span=300, count=25)
	r9 = ActionRule("bravo", priority=1)
	r10 = ActionRule("bravo", priority=2, span=300, count=25)
	r11 = ActionRule("bravo", priority=2, span=300, count=15)
	r12 = ActionRule("bravo", priority=2)

	s = sorted([r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12])
	assert s[0] == r2
	assert s[1] == r3
	assert s[2] == r1
	assert s[3] == r6
	assert s[4] == r4
	assert s[5] == r5
	assert s[6] == r7
	assert s[7] == r8
	assert s[8] == r9
	assert s[9] == r11
	assert s[10] == r10
	assert s[11] == r12


	s = ActionRule.sorted([r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12])
	assert s[0] == r6
	assert s[1] == r4
	assert s[2] == r5
	assert s[3] == r2
	assert s[4] == r3
	assert s[5] == r1
	assert s[6] == r11
	assert s[7] == r10
	assert s[8] == r12
	assert s[9] == r7
	assert s[10] == r8
	assert s[11] == r9

	# pass


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


def test_action_rule_hashing():
	r1 = ActionRule("alpha")
	r2 = ActionRule("alpha")

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 == h2

	r1 = ActionRule("alpha",span=5)
	r2 = ActionRule("alpha")

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 != h2

	r1 = ActionRule("alpha",span=5)
	r2 = ActionRule("alpha", span=5)

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 == h2

	r1 = ActionRule("alpha",span=5, count=7)
	r2 = ActionRule("alpha", span=5)

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 != h2

	r1 = ActionRule("alpha",span=5, count=7)
	r2 = ActionRule("alpha", span=5, count=7)

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 == h2

	r1 = ActionRule("alpha",span=5, count=7, priority=5)
	r2 = ActionRule("alpha", span=5, count=7)

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 != h2

	r1 = ActionRule("alpha",span=5, count=7, priority=5)
	r2 = ActionRule("alpha", span=5, count=7, priority=5)

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 == h2

	r1 = StationActionRule(
		"alpha",
		span=5,
		count=7,
		priority=5
	)
	r2 = ActionRule("alpha", span=5, count=7, priority=5)

	h1 = hash(r1)
	h2 = hash(r2)

	assert h1 != h2

def test_action_rule_set():
	r1 = ActionRule("alpha")
	r2 = ActionRule("alpha")

	s1: set[ActionRule] = set()
	s1.add(r1)

	assert not r1 is r2
	assert r2 in s1

	r2 = ActionRule("alpha", span=5)

	assert r2 not in s1

	s1.add(r2)

	r3 = ActionRule("alpha", span=5)

	assert not r3 is r1
	assert not r3 is r2
	assert r3 in s1

	r4 = ActionRule("alpha", span=5, count=7)

	assert r4 not in s1

	s1.add(r4)

	r5 = ActionRule("alpha", span=5, count=7)

	assert not r5 is r1
	assert not r5 is r2
	assert not r5 is r4
	assert r5 in s1

	r6 = ActionRule("alpha", span=5, count=7, priority=5)
	assert r6 not in s1

	s1.add(r6)

	r7 = ActionRule("alpha", span=5, count=7, priority=5)

	assert not r7 is r1
	assert not r7 is r2
	assert not r7 is r4
	assert not r7 is r6
	assert r7 in s1

	r8 = PathsActionRule(
		"alpha",
		span=5,
		count=7,
		priority=5,
	)

	assert r8 in s1
	#s1.add(r8)

	r9 = PathsActionRule(
		"alpha",
		span=5,
		count=7,
		priority=5
	)

	assert not r9 is r8
	assert r9 in s1

	r10 = PathsActionRule("alpha")

	assert r10 in s1

	r11 = PathsActionRule("alpha", path="bravo")

	assert r11 not in s1

	s1.add(r11)

	r12 = PathsActionRule("alpha", path="bravo")

	assert not r12 is r11
	assert r12 in s1

	r13 = PathsActionRule("bravo")

	assert r13 not in s1

	s1.add(r13)

	r14 = ActionRule("bravo")

	assert not r14 is r13
	assert r14 in s1

