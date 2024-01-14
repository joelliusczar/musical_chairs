import pytest
import bcrypt
from typing import Iterator, Any


side_effect_check = None

def test_bytes():
	s1 = b"this is my byte string"
	s2 = "this is my other string".encode()
	print(type(s1))
	print(type(s2))
	print("What do")

def test_bcrypt():
	mySalt = bcrypt.gensalt(12)
	hash = bcrypt.hashpw("my password string".encode(), mySalt)
	print(hash)
	testHash = bcrypt.hashpw("testPassword".encode(), mySalt)
	print(testHash)

@pytest.fixture
def fixture_side_effect() -> Iterator[None]:
	try:
		yield None
	finally:
		global side_effect_check
		assert side_effect_check

@pytest.mark.usefixtures("fixture_side_effect")
def test_use_side_effect():
	global side_effect_check
	side_effect_check = True



def getKeyedObjects():
	return [
		{
			"name": "bob",
			"id": "1",
			"owner": {
				"name": "bob",
				"id": "1",
			}
		},
		{
			"name": "1",
			"id": "2",
			"owner": {
				"name": "1",
				"id": "2",
			}
		},
		{
			"name": "ava",
			"id": "3",
			"owner": {
				"name": "2",
				"id": "3",
			}
		},
		{
			"name": "2",
			"id": "4",
			"owner": {
				"name": "g",
				"id": "4",
			}
		}
	]

def keyMatch(key: str, object: Any):

	if key == object["id"]:
		return True

	if key == object["name"]:
		return True
	return False


def pathToTestObject(path: str):
	keyedObjects = getKeyedObjects()
	split = path.split("/")
	selected = [s for s in keyedObjects \
		if keyMatch(split[1], s) and keyMatch(split[0],s["owner"])]
	return selected

def stringIdFind(key: str):
	keyedObjects = getKeyedObjects()
	selected = [s for s in keyedObjects \
		if keyMatch(key, s)]
	return selected

def testStringIdLogic():
	res = stringIdFind("1")
	res = stringIdFind("2")
	res = stringIdFind("3")
	res = stringIdFind("4")
	res = stringIdFind("bob")
	res = stringIdFind("ava")
	print(res)

def testKeyMatchingLogic():
	res = pathToTestObject("1/1")
	res = pathToTestObject("bob/bob")
	res = pathToTestObject("1/2")
	res = pathToTestObject("1/3")
	res = pathToTestObject("1/4")
	res = pathToTestObject("2/1")
	res = pathToTestObject("2/2")
	res = pathToTestObject("2/3")
	res = pathToTestObject("2/4")
	res = pathToTestObject("3/1")
	res = pathToTestObject("3/2")
	res = pathToTestObject("3/3")
	res = pathToTestObject("3/4")
	res = pathToTestObject("4/1")
	res = pathToTestObject("4/2")
	res = pathToTestObject("4/3")
	res = pathToTestObject("4/4")
	print(res)
	pass

@pytest.fixture
def read_request(request: pytest.FixtureRequest) -> int:
	return 0

def test_read_request(read_request: int):
	print(read_request)