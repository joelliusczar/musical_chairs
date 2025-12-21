from typing import Optional

num_rank_map = [
	*(str(i) for i in range(0, 10)),
	*(chr(ord("A") + i - 10) for i in range(10, 36)),
	*(chr(ord("a") + i - 36) for i in range(36, 62))
]

def digit_extract(digit: str) -> int:
	if digit >= "0" and digit <= "9":
		return ord(digit) - ord("0")
	if digit >= "A" and digit <= "Z":
		return ord(digit) - ord("A") + 10
	if digit >= "a" and digit <= "z":
		return ord(digit) - ord("a")  + 36
	raise RuntimeError(f"Out of range value: {digit}")


def convert_num(num: int) -> str:
	result = ""
	while num:
		digit = num % len(num_rank_map)
		result += num_rank_map[digit]
		num //= len(num_rank_map)
	return result[::-1]

def calc_order_next(before: Optional[str]) -> str:
	if not before:
		before = num_rank_map[0]
	lastDigit = before[-1]
	if lastDigit == "z":
		digits = [*reversed(before)]
		carry = 1
		power = 0
		if digits[-1] == "~":
			digits[-1] = ""
			power = digit_extract(digits[-2])
			digits[-2] = ""
		for idx in range(len(digits)):
			if not digits[idx]:
				continue
			if digits[idx] == "z":
				if carry:
					digits[idx] = "0"
					carry = 1
					continue
			elif carry:
				extractedNum = digit_extract(digits[idx]) + 1
				digits[idx] = num_rank_map[extractedNum]
			carry = 0
		if carry:
			digits.append("1")
			power += 1
		digits.append(num_rank_map[power])
		digits.append("~")
		return "".join(reversed(digits))
	else:
		extractedNum = digit_extract(lastDigit) + 1
		return before[:-1] + num_rank_map[extractedNum]	


'''
calc_order_between should only calculate the order only between values one 1 apart
Example, 0-1, 1-2. In other words, not 1-10
'''
def calc_order_between(
	before: Optional[str],
	after: Optional[str]
) -> str:
	if not before:
		before = num_rank_map[0]
	if not after:
		after = num_rank_map[-1]
	if before == after:
		return before + calc_order_between(None, None)
	result = ""
	before2 = before.ljust(len(after),"0")
	after2 = after.ljust(len(before), "0")
	remainder = 0 
	for idx in range(len(before2)):
		if before2[idx] == after2[idx]:
			result += before2[idx]
			continue
		beforeDigit = digit_extract(before2[idx])
		afterDigit = digit_extract(after2[idx])
		midPoint, remainder = divmod((beforeDigit + afterDigit), 2)
		if num_rank_map[midPoint] == "0":
			result += "0V"
		else:
			result += num_rank_map[midPoint]
	if remainder:
		result += num_rank_map[len(num_rank_map) // 2]
	return result