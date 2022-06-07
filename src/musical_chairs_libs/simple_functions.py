import unicodedata
from datetime import datetime, timezone

def get_datetime() -> datetime:
	return datetime.now(timezone.utc)

def format_name_for_save(username: str) -> str:
	if not username:
		return ""
	trimed = username.strip()
	normalized = unicodedata.normalize("NFC", trimed)
	return normalized

def format_name_for_search(username: str) -> str:
	if not username:
		return ""
	trimed = username.strip()
	normalized = unicodedata.normalize("NFKD", trimed)
	lower = normalized.lower()
	return lower
