from typing import Union, Optional

s2sDict = dict[str, str]
simpleDict = Union[
	dict[str, str],
	dict[str, Optional[str]],
	dict[str, Optional[Union[str, int]]],
	dict[str, Optional[Union[str, int, bool]]]
]