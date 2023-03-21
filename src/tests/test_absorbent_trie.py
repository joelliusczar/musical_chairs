
from musical_chairs_libs.dtos_and_utilities import AbsorbentTrie
from .helpers import get_sentences


trieWords = [
	"alpha",
	"alpine",
	"alpapcone",
	"alpenstock",
	"alprazolam",
	"alpacca",
	"argument",
	"album",
	"artist",
	"arts",
	"author",
	"accident",
	"acid",
	"acclimate",
	"ada",
	"altitude",
	"airplain",
	"arrow",
	"artisan",
	"arbor",
	"antenna",
	"armor",
	"atlanta",
	"angel",
	"angelic",
	"base",
	"basic",
	"bat",
	"bravo",
	"brave",
	"bravery",
	"boston",
	"bob",
	"branch",
	"bork",
	"bun",
	"bunk",
	"burnt",
	"brake",
	"bunt",
	"charlie",
	"chunk",
	"chuck",
	"char",
	"charizard",
	"candy",
	"cactus",
	"can",
	"curtain",
	"centuar",
	"century",
	"cent",
	"champion",
	"change",
	"chance",
	"cuss",
]


def test_path_trie_add_and_len():
	t = AbsorbentTrie()
	assert len(t) == 0

	added = t.add("a")
	assert added == 1
	assert len(t) == 1
	pathEnd = t.__get_path_end__("a")
	assert pathEnd != None
	assert len(pathEnd) == 0

	added = t.add("b")
	assert added == 1
	assert len(t) == 2
	pathEnd = t.__get_path_end__("b")
	assert pathEnd != None
	assert len(pathEnd) == 0

	added = t.add("ab")
	assert added == 1
	assert len(t) == 2
	pathEnd = t.__get_path_end__("a")
	assert pathEnd != None
	assert len(pathEnd) == 1

	added = t.add("abc")
	assert added == 1
	assert len(t) == 2
	pathEnd = t.__get_path_end__("ab")
	assert pathEnd != None
	assert len(pathEnd) == 1

	added = t.add("abd")
	assert added == 1
	assert len(t) == 3
	pathEnd = t.__get_path_end__("ab")
	assert pathEnd != None
	assert len(pathEnd) == 2

	added = t.add("ba")
	assert added == 1
	assert len(t) == 3
	pathEnd = t.__get_path_end__("b")
	assert pathEnd != None
	assert len(pathEnd) == 1

	added = t.add("abcd")
	assert added == 1
	assert len(t) == 3
	pathEnd = t.__get_path_end__("abc")
	assert pathEnd != None
	assert len(pathEnd) == 1

	added = t.add("cdef")
	assert added == 1
	assert len(t) == 4
	pathEnd = t.__get_path_end__("c")
	assert pathEnd != None
	assert len(pathEnd) == 1
	pathEnd = t.__get_path_end__("cd")
	assert pathEnd != None
	assert len(pathEnd) == 1
	pathEnd = t.__get_path_end__("cde")
	assert pathEnd != None
	assert len(pathEnd) == 1
	pathEnd = t.__get_path_end__("cdef")
	assert pathEnd != None
	assert len(pathEnd) == 0

	added = t.add("cde")
	assert added == 0
	assert len(t) == 4

	added = t.add("yes")
	assert added == 1
	assert len(t) == 5
	pathEnd = t.__get_path_end__("y")
	assert pathEnd != None
	assert len(pathEnd) == 1

	pathEnd = t.__get_path_end__("ye")
	assert pathEnd != None
	assert len(pathEnd) == 1

	pathEnd = t.__get_path_end__("yes")
	assert pathEnd != None
	assert len(pathEnd) == 0

	added = t.add("yetx")
	assert added == 1
	assert len(t) == 6

	pathEnd = t.__get_path_end__("y")
	assert pathEnd != None
	assert len(pathEnd) == 2

	pathEnd = t.__get_path_end__("ye")
	assert pathEnd != None
	assert len(pathEnd) == 2

	pathEnd = t.__get_path_end__("yes")
	assert pathEnd != None
	assert len(pathEnd) == 0

	pathEnd = t.__get_path_end__("yet")
	assert pathEnd != None
	assert len(pathEnd) == 1

	pathEnd = t.__get_path_end__("yetx")
	assert pathEnd != None
	assert len(pathEnd) == 0

	added = t.add("yetza")
	assert added == 1
	assert len(t) == 7

	pathEnd = t.__get_path_end__("y")
	assert pathEnd != None
	assert len(pathEnd) == 3

	pathEnd = t.__get_path_end__("ye")
	assert pathEnd != None
	assert len(pathEnd) == 3

	pathEnd = t.__get_path_end__("yes")
	assert pathEnd != None
	assert len(pathEnd) == 0

	pathEnd = t.__get_path_end__("yet")
	assert pathEnd != None
	assert len(pathEnd) == 2

	pathEnd = t.__get_path_end__("yetx")
	assert pathEnd != None
	assert len(pathEnd) == 0

	pathEnd = t.__get_path_end__("yetz")
	assert pathEnd != None
	assert len(pathEnd) == 1

	pathEnd = t.__get_path_end__("yetza")
	assert pathEnd != None
	assert len(pathEnd) == 0

def test_path_trie_extend():
	t = AbsorbentTrie()
	t.extend([
		"the",
		"the/fox/jumped/over/the/dog/",
		"the/dove/flew/over/the/fox",
		"damn/the/river",
		"the/fox/jumped/over/the/horse/",
		"damn/what/the/fuck",
		"tootle/le/zay/tootle/le/zay"
	])
	assert len(t) == 6

def test_trie_depth():
	t = AbsorbentTrie()
	assert t.depth == 0
	t.add("a")
	assert t.depth == 1
	t.add("b")
	assert t.depth == 1
	t.add("abc")
	assert t.depth == 3
	t.add("cb")
	assert t.depth == 3
	t.add("bcdefg")
	assert t.depth == 6

def test_path_end():
	t = AbsorbentTrie()
	t.extend(trieWords)
	pe = t.__get_path_end__("a")
	assert pe
	assert sorted(pe.keys) == sorted(["l","r","u","c","d","n","t","i"])
	pe = t.__get_path_end__("al")
	assert pe
	assert sorted(pe.keys) == sorted(["p","t","b"])

	pe = t.__get_path_end__("alp")
	assert pe
	assert sorted(pe.keys) == sorted(["i","h","a","r", "e"])

	pe = t.__get_path_end__("alpi")
	assert pe
	assert sorted(pe.keys) == sorted(["n"])

	pe = t.__get_path_end__("alpin")
	assert pe
	assert sorted(pe.keys) == sorted(["e"])

	pe = t.__get_path_end__("alpine")
	assert pe != None
	assert pe.keys == []

	pe = t.__get_path_end__("alpinex")
	assert pe == None

	pe = t.__get_path_end__("")
	assert pe == t

def test_iterate():
	t = AbsorbentTrie()
	t.add("alpha")
	t.add("album")
	t.add("alpine")
	t.add("artist")
	t.add("arts")
	t.add("angelic")
	t.add("bravery")
	t.add("bravo")
	t.add("bunk")
	t.add("bunt")

	l = list(t.paths_start_with("a"))
	assert l
	expected = sorted(["alpha","album","alpine","artist","arts","angelic"])
	assert sorted(l) == expected

def test_add_and_iterate():
	t = AbsorbentTrie()
	t.add("alpha")
	l = list(t.values())
	assert len(l) == 1

	t.add("alpine")
	l = list(t.values())
	assert len(l) == 2

	t.add("artist")
	l = list(t.values())
	assert len(l) == 3

	t.add("arts")
	l = list(t.values())
	assert len(l) == 4

	t.add("angel")
	l = list(t.values())
	assert len(l) == 5

	t.add("angelic")
	l = list(t.values())
	assert len(l) == 5
	assert "angel" not in l
	assert "angelic" in l

	t.add("bravery")
	l = list(t.values())
	assert len(l) == 6

	t.add("brave")
	l = list(t.values())
	assert len(l) == 6
	assert "brave" not in l
	assert "bravery" in l

	t.add("bravo")
	l = list(t.values())
	assert len(l) == 7
	assert "bravo" in l

	t.add("bun")
	l = list(t.values())
	assert len(l) == 8

	t.add("bunk")
	l = list(t.values())
	assert len(l) == 8
	assert "bun" not in l
	assert "bunk" in l

	t.add("bunt")
	l = list(t.values())
	assert len(l) == 9
	assert "bun" not in l
	assert "bunk" in l
	assert "bunt" in l


def test_path_trie_starts_with():
	t = AbsorbentTrie()
	t.extend([
		"the",
		"the/fox/jumped/over/the/dog/",
		"the/dove/flew/over/the/fox",
		"damn/the/river",
		"the/fox/jumped/over/the/horse/",
		"damn/what/the/fuck",
		"tootle/le/zay/tootle/le/zay"
	])
	t1 = list(t.paths_start_with("the"))
	assert len(t1) == 3
	t2 = list(t.paths_start_with("damn"))
	assert len(t2) == 2
	t3 = list(t.paths_start_with("the/fox"))
	assert len(t3) == 2
	pass


def test_trie_contains():
	t = AbsorbentTrie()
	t.extend(trieWords)
	assert "x" not in t
	assert "" in t
	assert "a" in t
	assert "b" in t
	assert "bu" in t
	assert "bun" in t
	assert "bunk" in t
	assert "bunt" in t
	assert "bur" in t
	assert "burn" in t
	assert "burne" not in t
	assert "burner" not in t
	assert "burnt" in t
	assert "burnts" not in t


def test_large_set():
	strs = get_sentences()
	t = AbsorbentTrie()
	t.extend(strs)
	list(t.paths_start_with(''))
