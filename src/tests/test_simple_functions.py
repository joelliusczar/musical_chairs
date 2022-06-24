from musical_chairs_libs.simple_functions import\
	seconds_to_tuple,\
	next_directory_level

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