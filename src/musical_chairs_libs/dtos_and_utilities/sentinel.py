

class Sentinel:

	def __init__(self, value: bool) -> None:
		self.value = value

	def __bool__(self) -> bool:
		return self.value

missing = Sentinel(False)
found = Sentinel(True)