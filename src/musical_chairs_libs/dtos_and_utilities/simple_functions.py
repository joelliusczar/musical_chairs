#pyright: reportMissingTypeStubs=false
import re
import bcrypt
import email_validator #pyright: ignore reportUnknownMemberType
import dataclasses
from datetime import datetime, timezone
from typing import (
	Any,
	Hashable,
	Iterable,
	Iterator,
	Optional,
	Tuple,
	overload,
	TypeVar,
	Union,
	Callable,
	cast
)
from email_validator import ValidatedEmail
from collections import Counter
from .type_aliases import (s2sDict)
from .lost_found import Lost
from .config_accessors import ConfigAcessors
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy.engine import Connection
from sqids import Sqids

T = TypeVar("T")

guidRegx = \
	r"[a-zA-Z\d]{8}-?[a-zA-Z\d]{4}-?[a-zA-Z\d]{4}-?[a-zA-Z\d]{4}-?[a-zA-Z\d]{12}"

def get_datetime() -> datetime:
	return datetime.now(timezone.utc)

def build_error_obj(msg: str, field: Optional[str]=None) -> dict[str, Any]:
	obj: dict[str, Any] = { "msg": msg, "field": field  }
	return obj

def hashpw(pw: bytes) -> bytes:
	return bcrypt.hashpw(pw, bcrypt.gensalt(12))

def checkpw(guess: bytes, hash: bytes) -> bool:
	return bcrypt.checkpw(guess, hash)

def validate_email(email: str) -> ValidatedEmail:
	return email_validator.validate_email(email, check_deliverability=False) #pyright: ignore reportUnknownMemberType

def seconds_to_tuple(seconds: int) -> Tuple[int, int, int, int]:
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	return (d, h, m, s)

def build_timespan_msg(timeleft: Tuple[int, int, int, int]) -> str:
	days = f"{timeleft[0]} days, " if any(timeleft[1:]) \
		else f"{timeleft[0]} days" if timeleft[0] else ""
	hours = f"{timeleft[1]} hours, " if any(timeleft[2:]) \
		else f"{timeleft[1]} hours" if timeleft[1] else ""
	minutes = f"{timeleft[2]} mins, " if timeleft[3] \
		else f"{timeleft[2]} mins" if timeleft[2] else ""
	seconds = f"and {timeleft[3]} seconds" \
		if any(timeleft[:-1]) else f"{timeleft[3]} seconds" if timeleft[3] else ""
	return f"{days}{hours}{minutes}{seconds}"

def get_duplicates(
	items: Iterable[Hashable]
) -> Iterator[Tuple[Hashable, int]]:
	counter = Counter(items)
	mostCommon = counter.most_common(1)
	return (pair for pair in mostCommon if pair[1] > 1)

def next_directory_level(path: str, prefix: Optional[str]="") -> str:
	if not prefix:
		prefix = ""
	matches = re.match(rf"({re.escape(prefix)}[^/]*/?)", path)
	if matches:
		groups = matches.groups()
		return groups[0] if groups else ""
	return ""

def get_non_simple_chars(name: str) -> Optional[str]:
		m = re.search(r"[^a-zA-Z0-9_\-]", name)
		if m:
			return m.group(0)
		return None

def is_name_safe(name: str, maxLen: int=50) -> bool:
	if len(name) > maxLen:
		return False
	if get_non_simple_chars(name):
		return False
	return True

def _kvpSplit(kvp: str) -> Tuple[str, str]:
	eqSplit = kvp.split("=")
	if len(eqSplit) < 2:
		return "name", kvp
	return eqSplit[0], eqSplit[1]

def role_dict(role: str) -> s2sDict:
		return {p[0]:p[1] for p in (_kvpSplit(k) for k in role.split(";"))}

@overload
def normalize_opening_slash(path: str, addSlash: bool=True) -> str:
	...

@overload
def normalize_opening_slash(path: None, addSlash: bool=True) -> None:
	...

def normalize_opening_slash(
	path: Optional[str],
	addSlash: bool=True
) -> Optional[str]:
	if path is None:
		return None
	if addSlash:
		if len(path) > 0 and path[0] == "/":
			return path
		return f"/{path}"
	if len(path) > 0 and path[0] != "/":
			return path
	return path[1:]


@overload
def normalize_closing_slash(path: str, addSlash: bool=True) -> str:
	...

@overload
def normalize_closing_slash(path: None, addSlash: bool=True) -> None:
	...

def normalize_closing_slash(
	path: Optional[str],
	addSlash: bool=True
) -> Optional[str]:
	if path is None:
		return None
	if addSlash:
		if len(path) > 0 and path[-1] == "/":
			return path
		return f"{path}/"
	if len(path) > 0 and path[-1] != "/":
			return path
	return path[:-1]

def squash_elements(
	compressura: Iterable[T],
	pattern: T
) -> Iterator[T]:
	cIter = iter(compressura)
	previous = next(cIter, Lost())
	if previous == Lost():
		return
	yield cast(T, previous)
	for element in cIter:
		if element == previous and element == pattern:
			continue
		previous = element
		yield element

def squash_chars(
	compressura: str,
	pattern: str
) -> str:
	return "".join(squash_elements(compressura, pattern))


def format_newlines_for_stream(input: str) -> str:
	cleaned = input.replace("\n", " ")
	output = f"{cleaned}\n"
	return output


def int_or_str(s: int | str) -> int | str:
	#fastapi/pydantic stopped auto comnverting my string ints
	#to ints
	try:
		i = int(s)
		return i
	except:
		return s


def int_or_default(s: int | str | None, default: int = 0) -> int:
	if not s:
		return default
	try:
		return int(s)
	except:
		return default


def interweave(
	it1: Iterable[T],
	it2: Iterable[T],
	compare: Callable[[T, T], bool]
) -> Iterator[T]:
	iter1 = iter(it1)
	iter2 = iter(it2)
	try:
		value1 = next(iter1)
	except StopIteration:
		yield from iter2
		return
	try:
		value2 = next(iter2)
	except StopIteration:
		yield value1
		yield from iter1
		return
	while True:
		if compare(value1, value2):
			yield value1
			try:
				value1 = next(iter1)
			except StopIteration:
				yield value2
				yield from iter2
				return
		else:
			yield value2
			try:
				value2 = next(iter2)
			except StopIteration:
				yield value1
				yield from iter1
				return

def __common_prefix__(s1: Iterable[T], s2: Iterable[T]) -> Iterable[T]:
	s2Iter = iter(s2)
	for e1 in s1:
		e2 = next(s2Iter, Lost())
		if e1 == e2:
			yield e1
		else:
			break

@overload
def common_prefix(s1: str, s2: str) -> str:
	...

@overload
def common_prefix(s1: Iterable[T], s2: Iterable[T]) -> Iterable[T]:
	...

def common_prefix(
	s1: Union[Iterable[T], str],
	s2: Union[Iterable[T], str]
) -> Union[Iterable[T], str]:

	if type(s1) == str and type(s2) == str:
		return "".join(__common_prefix__(s1, s2))
	elif not isinstance(s1, str) and not isinstance(s2, str):
		return __common_prefix__(s1, s2)
	else:
		raise ValueError(
			"Input types must either both be strings or both iterables"
		)

def guess_contenttype(filename: str) -> str:
	extension = Path(filename).suffix.casefold()
	if extension == ".mp3":
		return "audio/mpeg"
	elif extension == ".flac":
		return "audio/flac"
	elif extension == ".ogg":
		return "audio/ogg"

	return "application/octet-stream"

def clean_search_term_for_like(searchTerm: str) -> str:
	if not searchTerm:
		return ""
	return searchTerm.replace("_","\\_").replace("%","\\%")

def asdict(obj: Any, exclude: Optional[set[str]]=None) -> dict[str, Any]:
	d = dataclasses.asdict(obj)
	
	for key in (exclude or ()):
		del d[key]

	return d

@contextmanager
def open_transaction(conn: Connection):
	if conn.in_transaction():
		if transaction := conn.get_transaction():
			yield transaction
		else:
			raise RuntimeError("Ambiguous transaction availability")
	else:
		with conn.begin() as transaction:
			yield transaction


def encode_id(id: int) -> str:
	sqids = Sqids(
		alphabet=ConfigAcessors.shuffled_alphabet(),
		blocklist=[],
		min_length=10
	)
	return str(sqids.encode([id])) #pyright: ignore reportUnknownMemberType


def decode_id(id: str) -> int:
	sqids = Sqids(
		alphabet=ConfigAcessors.shuffled_alphabet(),
		blocklist=[],
		min_length=10
	)
	decoded = sqids.decode(id) #pyright: ignore reportUnknownMemberType
	if decoded:
		return int(decoded[0]) #pyright: ignore reportUnknownMemberType
	return 0

def decode_id_or_not[T](
	token: str | None,
	default: T | None = None
) -> int | T | None:
	if not token:
		return default
	decoded = decode_id(token)
	reencoded = encode_id(decoded)
	if reencoded == token:
		return decoded
	return default


