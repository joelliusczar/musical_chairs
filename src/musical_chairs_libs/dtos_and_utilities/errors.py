from .simple_functions import build_error_obj

class AlreadyUsedError(ValueError):
	
	@staticmethod
	def build_error(msg: str, field: str) -> "AlreadyUsedError":
		return AlreadyUsedError([build_error_obj(msg, field)])

class IllegalOperationError(RuntimeError):
	pass

class AlternateValueError(Exception):
	pass