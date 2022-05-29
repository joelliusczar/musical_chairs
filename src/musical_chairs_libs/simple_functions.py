from datetime import datetime, timezone

def get_datetime() -> datetime:
	return datetime.now(timezone.utc)
