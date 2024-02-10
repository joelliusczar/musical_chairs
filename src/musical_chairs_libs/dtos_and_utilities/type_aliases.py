from typing import (
	Union,
	Optional,
	TypeVar,
	Sequence,
	Set
)

T = TypeVar("T")

s2sDict = dict[str, str]
simpleDict = Union[
	dict[str, str],
	dict[str, Optional[str]],
	dict[str, Optional[Union[str, int]]],
	dict[str, Optional[Union[str, int, bool]]]
]

ReusableIterable = Union[Sequence[T],Set[T]]