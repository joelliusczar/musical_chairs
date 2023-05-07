import pytest
from typing import Any
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
	t = AbsorbentTrie[Any]()
	assert t.__node_count__ == 0

	t.add("a")
	assert t.__node_count__ == 1
	pathEnd = t.__node_at_path__("a")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	t.add("b")
	assert t.__node_count__ == 2
	pathEnd = t.__node_at_path__("b")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	t.add("ab")
	assert t.__node_count__ == 2
	pathEnd = t.__node_at_path__("a")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	t.add("abc")
	assert t.__node_count__ == 2
	pathEnd = t.__node_at_path__("ab")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	t.add("abd")
	assert t.__node_count__ == 3
	pathEnd = t.__node_at_path__("ab")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 2

	t.add("ba")
	assert t.__node_count__ == 3
	pathEnd = t.__node_at_path__("b")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	t.add("abcd")
	assert t.__node_count__ == 3
	pathEnd = t.__node_at_path__("abc")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	t.add("cdef")
	assert t.__node_count__ == 4
	pathEnd = t.__node_at_path__("c")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1
	pathEnd = t.__node_at_path__("cd")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1
	pathEnd = t.__node_at_path__("cde")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1
	pathEnd = t.__node_at_path__("cdef")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	t.add("cde")
	assert t.__node_count__ == 4

	t.add("yes")
	assert t.__node_count__ == 5
	pathEnd = t.__node_at_path__("y")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	pathEnd = t.__node_at_path__("ye")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	pathEnd = t.__node_at_path__("yes")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	t.add("yetx")
	assert t.__node_count__ == 6

	pathEnd = t.__node_at_path__("y")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 2

	pathEnd = t.__node_at_path__("ye")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 2

	pathEnd = t.__node_at_path__("yes")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	pathEnd = t.__node_at_path__("yet")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	pathEnd = t.__node_at_path__("yetx")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	t.add("yetza")
	assert t.__node_count__ == 7

	pathEnd = t.__node_at_path__("y")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 3

	pathEnd = t.__node_at_path__("ye")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 3

	pathEnd = t.__node_at_path__("yes")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	pathEnd = t.__node_at_path__("yet")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 2

	pathEnd = t.__node_at_path__("yetx")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

	pathEnd = t.__node_at_path__("yetz")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 1

	pathEnd = t.__node_at_path__("yetza")
	assert pathEnd != None
	assert pathEnd.__node_count__ == 0

def test_path_trie_extend():
	t = AbsorbentTrie[Any]()
	t.extend([
		"the",
		"the/fox/jumped/over/the/dog/",
		"the/dove/flew/over/the/fox",
		"damn/the/river",
		"the/fox/jumped/over/the/horse/",
		"damn/what/the/fuck",
		"tootle/le/zay/tootle/le/zay"
	])
	assert t.__node_count__ == 6

def test_trie_depth():
	t = AbsorbentTrie[Any]()
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
	t = AbsorbentTrie[Any]()
	t.extend(trieWords)
	pe = t.__node_at_path__("a")
	assert pe
	assert sorted(pe.child_keys) == sorted(["l","r","u","c","d","n","t","i"])
	pe = t.__node_at_path__("al")
	assert pe
	assert sorted(pe.child_keys) == sorted(["p","t","b"])

	pe = t.__node_at_path__("alp")
	assert pe
	assert sorted(pe.child_keys) == sorted(["i","h","a","r", "e"])

	pe = t.__node_at_path__("alpi")
	assert pe
	assert sorted(pe.child_keys) == sorted(["n"])

	pe = t.__node_at_path__("alpin")
	assert pe
	assert sorted(pe.child_keys) == sorted(["e"])

	pe = t.__node_at_path__("alpine")
	assert pe != None
	assert pe.child_keys == []
	with pytest.raises(KeyError):
		pe = t.__node_at_path__("alpinex")

	pe = t.__node_at_path__("")
	assert pe == t

def test_iterate():
	t = AbsorbentTrie[Any]()
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
	t = AbsorbentTrie[Any]()
	t.add("alpha")
	l = list(t.all_paths())
	assert len(l) == 1

	t.add("alpine")
	l = list(t.all_paths())
	assert len(l) == 2

	t.add("artist")
	l = list(t.all_paths())
	assert len(l) == 3

	t.add("arts")
	l = list(t.all_paths())
	assert len(l) == 4

	t.add("angel")
	l = list(t.all_paths())
	assert len(l) == 5

	t.add("angelic")
	l = list(t.all_paths())
	assert len(l) == 5
	assert "angel" not in l
	assert "angelic" in l

	t.add("bravery")
	l = list(t.all_paths())
	assert len(l) == 6

	t.add("brave")
	l = list(t.all_paths())
	assert len(l) == 6
	assert "brave" not in l
	assert "bravery" in l

	t.add("bravo")
	l = list(t.all_paths())
	assert len(l) == 7
	assert "bravo" in l

	t.add("bun")
	l = list(t.all_paths())
	assert len(l) == 8

	t.add("bunk")
	l = list(t.all_paths())
	assert len(l) == 8
	assert "bun" not in l
	assert "bunk" in l

	t.add("bunt")
	l = list(t.all_paths())
	assert len(l) == 9
	assert "bun" not in l
	assert "bunk" in l
	assert "bunt" in l

def test_path_trie_starts_with():
	t = AbsorbentTrie[Any]()
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
	t = AbsorbentTrie[Any]()
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
	t = AbsorbentTrie[Any]()
	t.extend(strs)
	list(t.paths_start_with(''))

def test_is_path_end():
	t = AbsorbentTrie[Any]()

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

	a = t.__node_at_path__("a")
	assert a != None
	assert a.is_path_end

	al = t.__node_at_path__("al")
	assert al != None
	assert not al.is_path_end

	alp = t.__node_at_path__("alp")
	assert alp != None
	assert not alp.is_path_end

	alph = t.__node_at_path__("alph")
	assert alph != None
	assert not alph.is_path_end

	alpha = t.__node_at_path__("alpha")
	assert alpha != None
	assert alpha.is_path_end

	alpi = t.__node_at_path__("alpi")
	assert alpi != None
	assert not alpi.is_path_end

	alpin = t.__node_at_path__("alpin")
	assert alpin != None
	assert not alpin.is_path_end

	alpine = t.__node_at_path__("alpine")
	assert alpine != None
	assert alpine.is_path_end

	ar = t.__node_at_path__("ar")
	assert ar != None
	assert not ar.is_path_end

	art = t.__node_at_path__("art")
	assert art != None
	assert not art.is_path_end

	arts = t.__node_at_path__("arts")
	assert arts != None
	assert arts.is_path_end

	arti = t.__node_at_path__("arti")
	assert arti != None
	assert not arti.is_path_end

	artis = t.__node_at_path__("artis")
	assert artis != None
	assert not artis.is_path_end

	artist = t.__node_at_path__("artist")
	assert artist != None
	assert artist.is_path_end

	an = t.__node_at_path__("an")
	assert an != None
	assert not an.is_path_end

	ang = t.__node_at_path__("ang")
	assert ang != None
	assert not ang.is_path_end

	ange = t.__node_at_path__("ange")
	assert ange != None
	assert not ange.is_path_end

	angel = t.__node_at_path__("angel")
	assert angel != None
	assert angel.is_path_end

	angeli = t.__node_at_path__("angeli")
	assert angeli != None
	assert not angeli.is_path_end

	angelic = t.__node_at_path__("angelic")
	assert angelic != None
	assert angelic.is_path_end

	b = t.__node_at_path__("b")
	assert b != None
	assert not b.is_path_end

	bu = t.__node_at_path__("bu")
	assert bu != None
	assert not bu.is_path_end

	bun = t.__node_at_path__("bun")
	assert bun != None
	assert bun.is_path_end

	bunt = t.__node_at_path__("bunt")
	assert bunt != None
	assert bunt.is_path_end

	bunk = t.__node_at_path__("bunk")
	assert bunk != None
	assert bunk.is_path_end

	y = t.__node_at_path__("y")
	assert y != None
	assert not y.is_path_end

	ye = t.__node_at_path__("ye")
	assert ye != None
	assert not ye.is_path_end

	yes = t.__node_at_path__("yes")
	assert yes != None
	assert yes.is_path_end

	yet = t.__node_at_path__("yet")
	assert yet != None
	assert not yet.is_path_end

	yetx = t.__node_at_path__("yetx")
	assert yetx != None
	assert yetx.is_path_end

	yetz = t.__node_at_path__("yetz")
	assert yetz != None
	assert not yetz.is_path_end

	yetza = t.__node_at_path__("yetza")
	assert yetza != None
	assert yetza.is_path_end

def test_is_prefix_for():
	t = AbsorbentTrie[Any]()
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

def test_closest_value_nodes():
	t = AbsorbentTrie[Any]()
	assert len(list(t.closest_value_nodes())) == 1

	t.add("ant")
	assert len(list(t.closest_value_nodes())) == 1
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	an = t.__node_at_path__("an")
	assert an != None and len(list(an.closest_value_nodes())) == 1
	ant = t.__node_at_path__("ant")
	assert ant != None and len(list(ant.closest_value_nodes())) == 1

	t.add("angel")
	assert len(list(t.closest_value_nodes())) == 2
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 2
	an = t.__node_at_path__("an")
	assert an != None and len(list(an.closest_value_nodes())) == 2
	ant = t.__node_at_path__("ant")
	assert ant != None and len(list(ant.closest_value_nodes())) == 1
	ang = t.__node_at_path__("ang")
	assert ang != None and len(list(ang.closest_value_nodes())) == 1
	ange = t.__node_at_path__("ange")
	assert ange != None and len(list(ange.closest_value_nodes())) == 1
	angel = t.__node_at_path__("angel")
	assert angel != None and len(list(angel.closest_value_nodes())) == 1

	t.add("a")
	assert len(list(t.closest_value_nodes())) == 1
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	an = t.__node_at_path__("an")
	assert an != None and len(list(an.closest_value_nodes())) == 2
	ant = t.__node_at_path__("ant")
	assert ant != None and len(list(ant.closest_value_nodes())) == 1

	t.add("bun")
	assert len(list(t.closest_value_nodes())) == 2
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	b = t.__node_at_path__("b")
	assert b != None and len(list(b.closest_value_nodes())) == 1

	t.add("bunk")
	assert len(list(t.closest_value_nodes())) == 2
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	an = t.__node_at_path__("an")
	assert an != None and len(list(an.closest_value_nodes())) == 2
	b = t.__node_at_path__("b")
	assert b != None and len(list(b.closest_value_nodes())) == 1
	bu = t.__node_at_path__("bu")
	assert bu != None and len(list(bu.closest_value_nodes())) == 1
	bun = t.__node_at_path__("bun")
	assert bun != None and len(list(bun.closest_value_nodes())) == 1

	t.add("bunt")
	assert len(list(t.closest_value_nodes())) == 2
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	an = t.__node_at_path__("an")
	assert an != None and len(list(an.closest_value_nodes())) == 2
	b = t.__node_at_path__("b")
	assert b != None and len(list(b.closest_value_nodes())) == 1
	bu = t.__node_at_path__("bu")
	assert bu != None and len(list(bu.closest_value_nodes())) == 1
	bun = t.__node_at_path__("bun")
	assert bun != None and len(list(bun.closest_value_nodes())) == 1

	t.add("yes")
	assert len(list(t.closest_value_nodes())) == 3
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	an = t.__node_at_path__("an")
	assert an != None and len(list(an.closest_value_nodes())) == 2
	b = t.__node_at_path__("b")
	assert b != None and len(list(b.closest_value_nodes())) == 1
	y = t.__node_at_path__("y")
	assert y != None and len(list(y.closest_value_nodes())) == 1

	t.add("yetx")
	assert len(list(t.closest_value_nodes())) == 4
	y = t.__node_at_path__("y")
	assert y != None and len(list(y.closest_value_nodes())) == 2
	ye = t.__node_at_path__("ye")
	assert ye != None and len(list(ye.closest_value_nodes())) == 2
	yes = t.__node_at_path__("yes")
	assert yes != None and len(list(yes.closest_value_nodes())) == 1
	yet = t.__node_at_path__("yet")
	assert yet != None and len(list(yet.closest_value_nodes())) == 1

	t.add("yetza")
	assert len(list(t.closest_value_nodes())) == 5
	y = t.__node_at_path__("y")
	assert y != None and len(list(y.closest_value_nodes())) == 3
	ye = t.__node_at_path__("ye")
	assert ye != None and len(list(ye.closest_value_nodes())) == 3
	yes = t.__node_at_path__("yes")
	assert yes != None and len(list(yes.closest_value_nodes())) == 1
	yet = t.__node_at_path__("yet")
	assert yet != None and len(list(yet.closest_value_nodes())) == 2


	t.add("artist")
	assert len(list(t.closest_value_nodes())) == 5
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	ar = t.__node_at_path__("ar")
	assert ar != None and len(list(ar.closest_value_nodes())) == 1

	t.add("arts")
	assert len(list(t.closest_value_nodes())) == 5
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	ar = t.__node_at_path__("ar")
	assert ar != None and len(list(ar.closest_value_nodes())) == 2
	art = t.__node_at_path__("art")
	assert art != None and len(list(art.closest_value_nodes())) == 2
	arts = t.__node_at_path__("arts")
	assert arts != None and len(list(arts.closest_value_nodes())) == 1
	arti = t.__node_at_path__("arti")
	assert arti != None and len(list(arti.closest_value_nodes())) == 1


	t.add("art")
	assert len(list(t.closest_value_nodes())) == 5
	a = t.__node_at_path__("a")
	assert a != None and len(list(a.closest_value_nodes())) == 1
	ar = t.__node_at_path__("ar")
	assert ar != None and len(list(ar.closest_value_nodes())) == 1
	art = t.__node_at_path__("art")
	assert art != None and len(list(art.closest_value_nodes())) == 1


def test_shortest_paths():
	t = AbsorbentTrie[Any]()
	t.extend(trieWords)
	shortest = sorted(t.shortest_paths())
	assert "alpha" in shortest
	assert "alpine" in shortest
	assert "alpapcone" in shortest
	assert "alpenstock" in shortest
	assert "alprazolam" in shortest
	assert "alpacca" in shortest
	assert "argument" in shortest
	assert "album" in shortest
	assert "artist" in shortest
	assert "arts" in shortest
	assert "author" in shortest
	assert "accident" in shortest
	assert "acid" in shortest
	assert "acclimate" in shortest
	assert "ada" in shortest
	assert "altitude" in shortest
	assert "airplain" in shortest
	assert "arrow" in shortest
	assert "artisan" in shortest
	assert "arbor" in shortest
	assert "antenna" in shortest
	assert "armor" in shortest
	assert "atlanta" in shortest
	assert "angel" in shortest
	assert "angelic" not in shortest
	assert "base" in shortest
	assert "basic" in shortest
	assert "bat" in shortest
	assert "bravo" in shortest
	assert "brave" in shortest
	assert "bravery" not in shortest
	assert "boston" in shortest
	assert "bob" in shortest
	assert "branch" in shortest
	assert "bork" in shortest
	assert "bun" in shortest
	assert "bunk" not in shortest
	assert "burnt" in shortest
	assert "brake" in shortest
	assert "bunt" not in shortest
	assert "charlie" not in shortest
	assert "chunk" in shortest
	assert "chuck" in shortest
	assert "char" in shortest
	assert "charizard" not in shortest
	assert "candy" not in shortest
	assert "cactus" in shortest
	assert "can" in shortest
	assert "curtain" in shortest
	assert "centuar" not in shortest
	assert "century" not in shortest
	assert "cent" in shortest
	assert "champion" in shortest
	assert "change" in shortest
	assert "chance" in shortest
	assert "cuss" in shortest

def test_values():
	t = AbsorbentTrie[Any]()
	t.extend((w, f"x_{w}_x") for w in [
		"alpha",
		"arts",
		"art",
		"artist",
		"artistic",
		"artisan",
		"a",
		"alpine",
		"ant",
		"arg",
		"argument",
		"argo",
		"argon"
	])
	results = list(t.values())
	aIdx = next(i for i in range(len(results)) \
		if results[i] == "x_a_x")
	alphaIdx = next(i for i in range(len(results)) \
		if results[i] == "x_alpha_x")
	artsIdx = next(i for i in range(len(results)) \
		if results[i] == "x_arts_x")
	artIdx = next(i for i in range(len(results)) \
		if results[i] == "x_art_x")
	artistIdx = next(i for i in range(len(results)) \
		if results[i] == "x_artist_x")
	artisticIdx = next(i for i in range(len(results)) \
		if results[i] == "x_artistic_x")
	artisanIdx = next(i for i in range(len(results)) \
		if results[i] == "x_artisan_x")
	alpineIdx = next(i for i in range(len(results)) \
		if results[i] == "x_alpine_x")
	antIdx = next(i for i in range(len(results)) \
		if results[i] == "x_ant_x")
	argIdx = next(i for i in range(len(results)) \
		if results[i] == "x_arg_x")
	argumentIdx = next(i for i in range(len(results)) \
		if results[i] == "x_argument_x")
	argoIdx = next(i for i in range(len(results)) \
		if results[i] == "x_argo_x")
	argonIdx = next(i for i in range(len(results)) \
		if results[i] == "x_argon_x")
	assert aIdx < argIdx
	assert aIdx < antIdx
	assert aIdx < artIdx
	assert argIdx < artsIdx
	assert antIdx < artsIdx
	assert artIdx < artsIdx

	assert argIdx < argoIdx
	assert antIdx < argoIdx
	assert artIdx < argoIdx

	assert artsIdx < alphaIdx
	assert argoIdx < alphaIdx

	assert artsIdx < argonIdx
	assert argoIdx < argonIdx

	assert alphaIdx < artistIdx
	assert argonIdx < artistIdx

	assert alphaIdx < alpineIdx
	assert argonIdx < alpineIdx

	assert artistIdx < artisanIdx
	assert alpineIdx < artisanIdx

	assert artisanIdx < artisticIdx
	assert artisanIdx < argumentIdx

def test_values_with_path():
	t = AbsorbentTrie[Any]()
	t.extend((w, f"x_{w}_x") for w in [
		"alpha",
		"arts",
		"art",
		"artist",
		"artistic",
		"artisan",
		"a",
		"alpine",
		"ant",
		"arg",
		"argument",
		"argo",
		"argon"
	])
	results = list(t.values("artsando"))
	assert "x_a_x" in results
	assert "x_art_x" in results
	assert "x_arts_x" in results
	assert len(results) == 3

	results = list(t.values("arti"))
	assert "x_a_x" in results
	assert "x_art_x" in results
	assert len(results) == 2