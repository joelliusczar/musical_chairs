from datetime import datetime, timezone
from typing import Any, Optional

def get_datetime() -> datetime:
	return datetime.now(timezone.utc)

def build_error_obj(msg: str, field: Optional[str]=None) -> dict[str, Any]:
	obj: dict[str, Any] = { "msg": msg }
	obj["field"] = field
	return obj
