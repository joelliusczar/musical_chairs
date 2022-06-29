from typing import\
	Any,\
	Optional
import unicodedata
from unidecode import unidecode

# moved from musical_chairs_libs/dtos.py

class SavedNameString:

	def __init__(self, value: Optional[str]) -> None:
		self._value = self.format_name_for_save(value)

	def __str__(self) -> str:
		return self._value

	def __len__(self) -> int:
		return len(self._value)

	def __eq__(self, o: Any) -> bool:
		return self._value == o

	@staticmethod
	def format_name_for_save(value: Optional[str]) -> str:
		if not value:
			return ""
		trimed = value.strip()
		return unicodedata.normalize("NFC", trimed)

class SearchNameString:

	def __init__(self, value: Optional[str]) -> None:
		self._value = self.format_name_for_search(value)

	def __str__(self) -> str:
		return self._value

	def __len__(self) -> int:
		return len(self._value)

	def __eq__(self, o: Any) -> bool:
		return self._value == o

	@staticmethod
	def format_name_for_search(
		value: Optional[str]
	) -> str:
		if not value:
			return ""
		transformed = unidecode(value, errors="preserve")
		trimed = transformed.strip()
		lower = trimed.lower()
		return lower