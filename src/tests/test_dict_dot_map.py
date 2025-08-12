from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	PathDict
)


def test_init_path_dict():
	p = PathDict()
	assert p is not None

def test_dict_dot_map_set():
	base = PathDict()
	base["a.b.c"] = 42
	assert base == {"a": {"b": {"c": 42}}}

def test_dict_dot_map_set_overwrite():
	base = PathDict({"a": {"b": {"c": 10}}})
	base["a.b.c"] = 42
	assert base == {"a": {"b": {"c": 42}}}

def test_dict_dot_map_set_create_new_path():
	base = PathDict({"a": {"b": {}}})
	base["a.b.d"] = 99
	assert base == {"a": {"b": {"d": 99}}}

def test_dict_dot_map_get_existing_path():
	base = PathDict({"a": {"b": {"c": 42}}})
	result = base["a.b.c"]
	assert result == 42

def test_dict_dot_map_get_non_existing_path_with_default():
	base = PathDict({"a": {"b": {"c": 42}}})
	result = base.get("a.b.d", default=99)
	assert result == 99

def test_dict_dot_map_unflatten_with_omit_nulls_true():
	paths: dict[str, Any] = {
		"a.b.c": 42,
		"a.b.d": None,
		"x.y.z": 99,
		"x.y.w": None,
		"x.m.a": None,
	}
	result = PathDict(paths, omitNulls=True)
	assert result == {
		"a": {"b": {"c": 42}},
		"x": {"y": {"z": 99}}
	}

def test_dict_contains():
	paths: dict[str, Any] = {
		"a.b.c": 42,
		"a.b.d": None,
		"x.y.z": 99,
		"x.y.w": None,
		"x.m.a": None,
	}
	pathsDict = PathDict(paths, omitNulls=True)
	assert "a.b.c" in pathsDict
	assert "a.b" in pathsDict
	assert "a" in pathsDict
	assert "" not in pathsDict
	assert "a.b.e" not in pathsDict

def test_dict_splat():
	paths: dict[str, Any] = {
		"a.b.c": 42,
		"a.b.d": None,
		"x.y.z": 99,
		"x.y.w": None
	}
	pathDict = PathDict(paths, omitNulls=False)
	result = {**pathDict}
	assert result == {
		"a": {"b": {"c": 42, "d": None}},
		"x": {"y": {"z": 99, "w": None}}
	}



def test_dict_dot_map_unflatten_with_omit_nulls_false():
	paths: dict[str, Any] = {
		"a.b.c": 42,
		"a.b.d": None,
		"x.y.z": 99,
		"x.y.w": None
	}
	result = PathDict(paths, omitNulls=False)
	assert result == {
		"a": {"b": {"c": 42, "d": None}},
		"x": {"y": {"z": 99, "w": None}}
	}

def test_dict_dot_map_get_non_existing_path_without_default():
	base = PathDict({"a": {"b": {"c": 42}}})
	try:
		base["a.b.d"]
	except KeyError as e:
		assert str(e) == "'a.b.d not found'"
	else:
		assert False, "Expected KeyError was not raised"