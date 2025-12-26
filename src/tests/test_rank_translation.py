from musical_chairs_libs.dtos_and_utilities import (
	calc_order_between,
	convert_num,
	calc_order_next,
)

	
def test_calc_insert():
	assert calc_order_between("0", "1") == "0V" #/2
	assert calc_order_between("0", "0F") == "07" #/8
	assert calc_order_between("0", "07") == "03" #/8
	assert calc_order_between("0", "03") == "01" #/8
	assert calc_order_between("0", "01") == "00V" #/8
	assert calc_order_between("0", "00V") == "00F" #/8
	assert calc_order_between("0", "00F") == "007" #/16
	assert calc_order_between("0", "007") == "003"
	assert calc_order_between("0", "003") == "001"
	assert calc_order_between("0", "001") == "000V"
	assert calc_order_between("1", "1") == "1U"
	assert calc_order_between("1", "2") == "1V"
	assert calc_order_between("1", "1V") == "1F"#"1F" #3
	assert calc_order_between("1", "1F") == "17" #"17" #4
	assert calc_order_between("1", "17") == "13" #"17" #4
	assert calc_order_between("1", "13") == "11" #"13" #5
	assert calc_order_between("1", "11") == "10V" #"11" #6
	assert calc_order_between("1", "10V") == "10F" #"10F" #8
	assert calc_order_between("1", "10F") == "107" #9
	assert calc_order_between("1", "107") == "103" #10
	assert calc_order_between("1", "103") == "101" #11
	assert calc_order_between("1", "101") == "100V" #12
	assert calc_order_between("1F", "1V") == "1N"
	assert calc_order_between("1F", "1N") == "1J"
	assert calc_order_between("1F", "1J") == "1H"
	assert calc_order_between("1F", "1H") == "1G"
	assert calc_order_between("1F", "1G") == "1FV"
	assert calc_order_between("1F", "1FV") == "1FF" #"1FF"

	# assert calc_order_between(None, None) == "U"
	assert calc_order_between("1", "3") == "2"
	assert calc_order_between("001", "002") == "001V"
	assert calc_order_between("01", "03") == "02"
	assert calc_order_between("01", "04") == "02" #*
	assert calc_order_between("01", "05") == "03"
	assert calc_order_between("01", "06") == "03"
	assert calc_order_between("01", "07") == "04"
	assert calc_order_between("01", "08") == "04"
	assert calc_order_between("01", "09") == "05"
	assert calc_order_between("01", "0A") == "05"
	assert calc_order_between("1", "A") == "5"
	assert calc_order_between("1", "Z") == "I"
	assert calc_order_between("1", "z") == "V"
	assert calc_order_between("01", "0z") == "0V"
	# assert calc_order_between("01", "10") == "0V"

def test_num_to_rank():
	assert convert_num(0) == ""
	assert convert_num(1) == "1"
	assert convert_num(2) == "2"
	assert convert_num(9) == "9"
	assert convert_num(10) == "A"
	assert convert_num(11) == "B"
	assert convert_num(35) == "Z"
	assert convert_num(36) == "a"
	assert convert_num(37) == "b"
	assert convert_num(60) == "y"
	assert convert_num(61) == "z"
	assert convert_num(62) == "10"
	assert convert_num(63) == "11"
	assert convert_num(64) == "12"
	assert convert_num(69) == "17"
	assert convert_num(71) == "19"
	assert convert_num(72) == "1A"
	assert convert_num(73) == "1B"
	assert convert_num(97) == "1Z"
	assert convert_num(98) == "1a"
	assert convert_num(123) == "1z"
	assert convert_num(124) == "20"

def test_calc_order_next():
	assert calc_order_next("0") == "1"
	assert calc_order_next("1") == "2"
	assert calc_order_next("9") == "A"
	assert calc_order_next("Z") == "a"
	assert calc_order_next("z") == "~110"
	assert calc_order_next("~110") == "~111"
	assert calc_order_next("~111") == "~112"
	assert calc_order_next("~119") == "~11A"
	assert calc_order_next("~11Z") == "~11a"
	assert calc_order_next("~11z") == "~120"
	assert calc_order_next("~120") == "~121"
	assert calc_order_next("~12z") == "~130"
	assert calc_order_next("~1Az") == "~1B0"
	assert calc_order_next("~1az") == "~1b0"
	assert calc_order_next("~1zy") == "~1zz"
	assert calc_order_next("~1zz") == "~2100"
	assert calc_order_next("~2109") == "~210A"
	assert calc_order_next("~210Z") == "~210a"
	assert calc_order_next("~210z") == "~2110"
	assert calc_order_next("~2119") == "~211A"
	assert calc_order_next("~211z") == "~2120"
	assert calc_order_next("~212z") == "~2130"
	assert calc_order_next("~2900") == "~2901"
	assert calc_order_next("~29zz") == "~2A00"
	assert calc_order_next("~2Zzz") == "~2a00"
	assert calc_order_next("~2zzz") == "~31000"
	assert calc_order_next("~310zz") == "~31100"
	assert calc_order_next("~3110z") == "~31110"

# def test_ordering():
# 	word = "1"
# 	arr: list[str] = ["" * 10]
# 	for idx in range(0, 62**4):
# 		arr[idx % len(arr)] = word
# 		word = calc_order_next(word)
	
# 	s =  sorted(arr)
# 	pass
