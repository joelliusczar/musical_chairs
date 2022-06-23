#pyright: reportMissingTypeStubs=false
import bcrypt
import email_validator #pyright: ignore reportUnknownMemberType
from datetime import datetime, timezone
from typing import Any, Optional, Tuple
from email_validator import ValidatedEmail

class DatetimeGetter:
	def __init__(self, currentDateTime: Optional[datetime]=None) -> None:
		self.overrideDate = currentDateTime

	def __call__(self) -> datetime:
		if self.overrideDate:
			return self.overrideDate
		return datetime.now(timezone.utc)


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