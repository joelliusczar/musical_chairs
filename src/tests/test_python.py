import bcrypt

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