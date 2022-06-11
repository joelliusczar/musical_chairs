from datetime import datetime, timezone
from typing import Any

def get_datetime() -> datetime:
	return datetime.now(timezone.utc)

def build_error_obj(msg: str) -> dict[str, Any]:
	return { "msg": msg }
