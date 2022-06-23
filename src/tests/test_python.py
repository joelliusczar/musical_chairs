from typing import Iterator
import pytest
import bcrypt

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

@pytest.fixture
def fixture_side_effect() -> Iterator[None]:
	try:
		yield None
	finally:
		print("finally")
		global side_effect_check
		assert side_effect_check

@pytest.mark.usefixtures("fixture_side_effect")
def test_use_side_effect():
	print("get started")
	global side_effect_check
	side_effect_check = True
	print("done here")

