from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	seconds_to_tuple,
	next_directory_level,
	squash_sequential_duplicate_chars,
	interweave,
	common_prefix
)
from sqlalchemy.engine import Connection
from sqlalchemy import\
	select
from sqlalchemy.sql import ColumnCollection
from .common_fixtures import *
from musical_chairs_libs.tables import songs as songs_tbl, sg_path

sg: ColumnCollection = songs_tbl.columns #pyright: ignore reportUnknownMemberType
sg_pk: Any = sg.pk #pyright: ignore reportUnknownMemberType
sg_name: Any = sg.name #pyright: ignore reportUnknownMemberType

def test_seconds_to_tuple():
	result = seconds_to_tuple(59)
	assert result[0] == 0
	assert result[1] == 0
	assert result[2] == 0
	assert result[3] == 59

	result = seconds_to_tuple(60)
	assert result[0] == 0
	assert result[1] == 0
	assert result[2] == 1
	assert result[3] == 0

	result = seconds_to_tuple(61)
	assert result[0] == 0
	assert result[1] == 0
	assert result[2] == 1
	assert result[3] == 1

	result = seconds_to_tuple(119)
	assert result[0] == 0
	assert result[1] == 0
	assert result[2] == 1
	assert result[3] == 59

	result = seconds_to_tuple(120)
	assert result[0] == 0
	assert result[1] == 0
	assert result[2] == 2
	assert result[3] == 0

	result = seconds_to_tuple(3599)
	assert result[0] == 0
	assert result[1] == 0
	assert result[2] == 59
	assert result[3] == 59

	result = seconds_to_tuple(3600)
	assert result[0] == 0
	assert result[1] == 1
	assert result[2] == 0
	assert result[3] == 0

	result = seconds_to_tuple(3601)
	assert result[0] == 0
	assert result[1] == 1
	assert result[2] == 0
	assert result[3] == 1

	result = seconds_to_tuple(86399)
	assert result[0] == 0
	assert result[1] == 23
	assert result[2] == 59
	assert result[3] == 59

	result = seconds_to_tuple(86400)
	assert result[0] == 1
	assert result[1] == 0
	assert result[2] == 0
	assert result[3] == 0

	result = seconds_to_tuple(86401)
	assert result[0] == 1
	assert result[1] == 0
	assert result[2] == 0
	assert result[3] == 1

	result = seconds_to_tuple(2678400)
	assert result[0] == 31
	assert result[1] == 0
	assert result[2] == 0
	assert result[3] == 0

def test_next_directory_level():
	path = "Pop/Pop_A-F/Beatles,_The/Abbey_Road/"\
		"01._Come_Together_-_The_Beatles.flac"
	result = next_directory_level(path)
	assert result == "Pop/"
	result = next_directory_level(path, "P")
	assert result == "Pop/"
	result = next_directory_level(path, "Pop")
	assert result == "Pop/"
	result = next_directory_level(path, "Pop/")
	assert result == "Pop/Pop_A-F/"
	result = next_directory_level(path, "Pop/Pop")
	assert result == "Pop/Pop_A-F/"
	result = next_directory_level(path, "Pop/Pop_A-")
	assert result == "Pop/Pop_A-F/"
	result = next_directory_level(path, "Pop/Pop_A-F")
	assert result == "Pop/Pop_A-F/"
	result = next_directory_level(path, "Pop/Pop_A-F/")
	assert result == "Pop/Pop_A-F/Beatles,_The/"
	result = next_directory_level(path, "Pop/Pop_A-F/Beatles,_The/")
	assert result == "Pop/Pop_A-F/Beatles,_The/Abbey_Road/"
	result = next_directory_level(path, "Pop/Pop_A-F/Beatles,_The/Abbey_Road/")
	assert result == "Pop/Pop_A-F/Beatles,_The/Abbey_Road/"\
		"01._Come_Together_-_The_Beatles.flac"
	path = "/Pop/Pop_A-F/Beatles,_The/Abbey_Road/"\
		"01._Come_Together_-_The_Beatles.flac"
	result = next_directory_level(path)
	pass
	


def test_populate_model_from_datarow(fixture_conn_cardboarddb: Connection):
	conn = fixture_conn_cardboarddb
	query = select(sg_pk.label("id"), sg_name, sg_path)
	row = conn.execute(query).fetchone() #pyright: ignore reportUnknownMemberType
	print("oh hai")

def test_squash_sequential_duplicates():
	result = squash_sequential_duplicate_chars("/alpha//bravo","/")
	assert result == "/alpha/bravo"

	result = squash_sequential_duplicate_chars("alpha//bravo","/")
	assert result == "alpha/bravo"


	result = squash_sequential_duplicate_chars("//////alpha//bravo","/")
	assert result == "/alpha/bravo"

	result = squash_sequential_duplicate_chars("//////","/")
	assert result == "/"

	result = squash_sequential_duplicate_chars("//////alpha//bravo////","/")
	assert result == "/alpha/bravo/"

def test_interweave():
	arr1: list[int] = []
	arr2: list[int] = []
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == []

	arr1 = [1]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1]

	arr2 = [2]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2]

	arr1 = [1, 3]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3]

	arr2 = [2, 4]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3, 4]

	arr1 = [1, 3, 9]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3, 4, 9]

	arr2 = [2, 4, 6, 8]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3, 4, 6, 8, 9]

	arr1 = [1, 3, 9, 13, 15, 17, 19, 21, 23, 25]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3, 4, 6, 8, 9, 13, 15, 17, 19, 21, 23, 25]

	arr2 = [2, 4, 6, 8, 26, 28, 30, 32, 34, 36, 38, 40]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [
		1, 2, 3, 4, 6, 8, 9, 13, 15, 17, 19, 21, 23, 25, 26, 28, 30, 32, 
		34, 36, 38, 40
	]

	arr1 = [1, 3, 9, 13, 15, 17, 19, 21, 23, 25, 33]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [
		1, 2, 3, 4, 6, 8, 9, 13, 15, 17, 19, 21, 23, 25, 26, 28, 30, 32, 
		33, 34, 36, 38, 40
	]

	arr1 = [1, 2, 3, 4, 5]
	arr2 = [6, 7, 8, 9, 10]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

	result = list(interweave(arr2, arr1, lambda x, y: x < y))
	assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

	arr1 = [1, 2, 3, 4, 6]
	arr2 = [5]
	result = list(interweave(arr1, arr2, lambda x, y: x < y))
	assert result == [1, 2, 3, 4, 5, 6]

def test_common_prefix():
	result = common_prefix("different", "no shared")
	assert result == ""

	result = common_prefix("astart", "almost")
	assert result == "a"

	result = common_prefix("astart", "ass")
	assert result == "as"

	result = common_prefix("astart", "asst")
	assert result == "as"

	result = common_prefix("astart", "astar")
	assert result == "astar"

	result = common_prefix("ast", "astar")
	assert result == "ast"

	result = common_prefix("astr", "astar")
	assert result == "ast"

	result = common_prefix("astronomy", "astrology")
	assert result == "astro"