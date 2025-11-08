class Eitherton:
	__my_instance__ = None

	def __new__(cls):
		if cls.__my_instance__ is None:
			cls.__my_instance__ = super().__new__(cls)
		return cls.__my_instance__ 


class Lost(Eitherton):
	def __bool__(self) -> bool:
		return False

	def __repr__(self) -> str:
		return "Lost"


class Found(Eitherton):
	def __bool__(self) -> bool:
		return True

	def __repr__(self) -> str:
		return "Found"