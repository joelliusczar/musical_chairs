#pyright: reportMissingTypeStubs=false
import bcrypt
import email_validator #pyright: ignore reportUnknownMemberType
from datetime import datetime, timezone
from typing import Any, Optional
from email_validator import ValidatedEmail

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