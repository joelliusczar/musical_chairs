from typing import\
	Any,\
	Callable

# moved from musical_chairs_libs/dtos.py
def min_length_validator_factory(
	minLen: int,
	field: str
) -> Callable[[Any, str], str]:
	def _validator(cls: Any, v: str) -> str:
		if len(v) < minLen:
			raise ValueError(f"{field} does not meet the length requirement\n"
				f"Mininum Length {minLen}. your {field.lower()} length: {len(v)}"
			)
		return v
	return _validator