



class Sentinel:

	def __bool__(self) -> bool:
		return False

missing = Sentinel()