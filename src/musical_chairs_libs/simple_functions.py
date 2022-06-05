import unicodedata
from datetime import datetime, timezone

def get_datetime() -> datetime:
	return datetime.now(timezone.utc)

def format_user_name(username: str) -> str:
	if not username:
		return ""
	trimed = username.strip()
	normalized = unicodedata.normalize("NFC", trimed)
	lower = normalized.lower()
	return lower
