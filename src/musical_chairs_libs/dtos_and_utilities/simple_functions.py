#pyright: reportMissingTypeStubs=false
import re
import bcrypt
import email_validator #pyright: ignore reportUnknownMemberType
from datetime import datetime, timezone
from typing import (
	Any,
	Hashable,
	Iterable,
	Iterator,
	Optional,
	Tuple
)
from email_validator import ValidatedEmail
from collections import Counter
from .type_aliases import (s2sDict)


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
	return email_validator.validate_email(email) #pyright: ignore reportUnknownMemberType

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

def check_name_safety(name: str) -> Optional[str]:
		m = re.search(r"\W", name)
		if m:
			return m.group(0)
		return None

def _kvpSplit(kvp: str) -> Tuple[str, str]:
	eqSplit = kvp.split("=")
	if len(eqSplit) < 2:
		return "name", kvp
	return eqSplit[0], eqSplit[1]

def role_dict(role: str) -> s2sDict:
		return {p[0]:p[1] for p in (_kvpSplit(k) for k in role.split(";"))}

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
