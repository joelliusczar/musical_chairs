
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

def test_is_path_end():
	t = AbsorbentTrie()

	t.add("a")
	t.add("alpha")
	t.add("alpine")
	t.add("artist")
	t.add("arts")
	t.add("angel")
	t.add("angelic")
	t.add("bun")
	t.add("bunk")
	t.add("bunt")
	t.add("yes")
	t.add("yetx")
	t.add("yetza")

	a = t.__get_path_end__("a")
	assert a != None
	assert a.is_path_end

	al = t.__get_path_end__("al")
	assert al != None
	assert not al.is_path_end

	alp = t.__get_path_end__("alp")
	assert alp != None
	assert not alp.is_path_end

	alph = t.__get_path_end__("alph")
	assert alph != None
	assert not alph.is_path_end

	alpha = t.__get_path_end__("alpha")
	assert alpha != None
	assert alpha.is_path_end

	alpi = t.__get_path_end__("alpi")
	assert alpi != None
	assert not alpi.is_path_end

	alpin = t.__get_path_end__("alpin")
	assert alpin != None
	assert not alpin.is_path_end

	alpine = t.__get_path_end__("alpine")
	assert alpine != None
	assert alpine.is_path_end

	ar = t.__get_path_end__("ar")
	assert ar != None
	assert not ar.is_path_end

	art = t.__get_path_end__("art")
	assert art != None
	assert not art.is_path_end

	arts = t.__get_path_end__("arts")
	assert arts != None
	assert arts.is_path_end

	arti = t.__get_path_end__("arti")
	assert arti != None
	assert not arti.is_path_end

	artis = t.__get_path_end__("artis")
	assert artis != None
	assert not artis.is_path_end

	artist = t.__get_path_end__("artist")
	assert artist != None
	assert artist.is_path_end

	an = t.__get_path_end__("an")
	assert an != None
	assert not an.is_path_end

	ang = t.__get_path_end__("ang")
	assert ang != None
	assert not ang.is_path_end

	ange = t.__get_path_end__("ange")
	assert ange != None
	assert not ange.is_path_end

	angel = t.__get_path_end__("angel")
	assert angel != None
	assert angel.is_path_end

	angeli = t.__get_path_end__("angeli")
	assert angeli != None
	assert not angeli.is_path_end

	angelic = t.__get_path_end__("angelic")
	assert angelic != None
	assert angelic.is_path_end

	b = t.__get_path_end__("b")
	assert b != None
	assert not b.is_path_end

	bu = t.__get_path_end__("bu")
	assert bu != None
	assert not bu.is_path_end

	bun = t.__get_path_end__("bun")
	assert bun != None
	assert bun.is_path_end

	bunt = t.__get_path_end__("bunt")
	assert bunt != None
	assert bunt.is_path_end

	bunk = t.__get_path_end__("bunk")
	assert bunk != None
	assert bunk.is_path_end

	y = t.__get_path_end__("y")
	assert y != None
	assert not y.is_path_end

	ye = t.__get_path_end__("ye")
	assert ye != None
	assert not ye.is_path_end

	yes = t.__get_path_end__("yes")
	assert yes != None
	assert yes.is_path_end

	yet = t.__get_path_end__("yet")
	assert yet != None
	assert not yet.is_path_end

	yetx = t.__get_path_end__("yetx")
	assert yetx != None
	assert yetx.is_path_end

	yetz = t.__get_path_end__("yetz")
	assert yetz != None
	assert not yetz.is_path_end

	yetza = t.__get_path_end__("yetza")
	assert yetza != None
	assert yetza.is_path_end

def test_is_prefix_for():
	t = AbsorbentTrie()
	t.extend(trieWords)

	res = t.has_prefix_for("alpa")
	assert not res

	res = t.has_prefix_for("a")
	assert not res

	res = t.has_prefix_for("ac")
	assert not res

	res = t.has_prefix_for("aci")
	assert not res

	res = t.has_prefix_for("acid")
	assert res

	res = t.has_prefix_for("acidic")
	assert res

	res = t.has_prefix_for("acidification")
	assert res

	res = t.has_prefix_for("cussing")
	assert res

	res = t.has_prefix_for("h")
	assert not res

	res = t.has_prefix_for("ha")
	assert not res

	res = t.has_prefix_for("han")
	assert not res

	res = t.has_prefix_for("hank")
	assert not res


