from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	DictDotMap
)


def test_dict_dot_map_set():
	base: dict[str, Any] = {}
	DictDotMap.set(base, "a.b.c", 42)
	assert base == {"a": {"b": {"c": 42}}}

def test_dict_dot_map_set_overwrite():
	base: dict[str, Any] = {"a": {"b": {"c": 10}}}
	DictDotMap.set(base, "a.b.c", 42)
	assert base == {"a": {"b": {"c": 42}}}

def test_dict_dot_map_set_create_new_path():
	base: dict[str, Any] = {"a": {"b": {}}}
	DictDotMap.set(base, "a.b.d", 99)
	assert base == {"a": {"b": {"d": 99}}}

def test_dict_dot_map_get_existing_path():
	base: dict[str, Any] = {"a": {"b": {"c": 42}}}
	result = DictDotMap.get(base, "a.b.c")
	assert result == 42

def test_dict_dot_map_get_non_existing_path_with_default():
	base: dict[str, Any] = {"a": {"b": {"c": 42}}}
	result = DictDotMap.get(base, "a.b.d", default=99)
	assert result == 99

def test_dict_dot_map_unflatten_with_omit_nulls_true():
	paths: dict[str, Any] = {
		"a.b.c": 42,
		"a.b.d": None,
		"x.y.z": 99,
		"x.y.w": None,
		"x.m.a": None,
	}
	result = DictDotMap.unflatten(paths, omitNulls=True)
	assert result == {
		"a": {"b": {"c": 42}},
		"x": {"y": {"z": 99}}
	}

def test_dict_dot_map_unflatten_with_omit_nulls_false():
	paths: dict[str, Any] = {
		"a.b.c": 42,
		"a.b.d": None,
		"x.y.z": 99,
		"x.y.w": None
	}
	result = DictDotMap.unflatten(paths, omitNulls=False)
	assert result == {
		"a": {"b": {"c": 42, "d": None}},
		"x": {"y": {"z": 99, "w": None}}
	}

def test_dict_dot_map_get_non_existing_path_without_default():
	base: dict[str, Any] = {"a": {"b": {"c": 42}}}
	try:
		DictDotMap.get(base, "a.b.d")
	except KeyError as e:
		assert str(e) == "'a.b.d not found'"
	else:
		assert False, "Expected KeyError was not raised"