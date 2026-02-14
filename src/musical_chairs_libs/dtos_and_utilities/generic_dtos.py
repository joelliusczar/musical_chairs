from typing import (
	List,
	TypeVar,
	Generic,
	Optional,
	cast,
)
from pydantic import (
	BaseModel as MCBaseClass,
	ConfigDict,
	Field,
	field_validator
)
from .action_rule_dtos import ActionRule
from .simple_functions import (encode_id, decode_id)


T = TypeVar("T")

class FrozenBaseClass(MCBaseClass):
	model_config = ConfigDict(frozen=True)

class ListData(MCBaseClass, Generic[T]):
	items: List[T]


class TableData(ListData[T]):
	totalrows: int


# class ErrorInfo(BaseModel):
# 	msg: str

class FrozenIdItem(FrozenBaseClass):
	id: int


class FrozenTokenItem(FrozenBaseClass):
	id: str

	@field_validator("id", mode="before")
	@classmethod
	def encoded_id(cls, raw: int | str) -> str:
		if isinstance(raw, str):
			return raw
		else:
			return encode_id(raw)


	def decoded_id(self) -> int:
		return decode_id(self.id)


class FrozenNamed(FrozenBaseClass):
	name: str


class FrozenNamedIdItem(FrozenIdItem, FrozenNamed):
	...


class FrozenNamedTokenItem(FrozenTokenItem, FrozenNamed):
	...


class TokenItem(MCBaseClass):
	id: str=Field(frozen=True)

	@field_validator("id", mode="before")
	@classmethod
	def encoded_id(cls, raw: int | str) -> str:
		if isinstance(raw, str):
			return raw
		else:
			return encode_id(raw)


	def decoded_id(self) -> int:
		return decode_id(self.id)


class IdItem(MCBaseClass):
	id: int=Field(frozen=True)

	@field_validator("id", mode="before")
	@classmethod
	def decode_id(cls, raw: int | str) -> int:
		if isinstance(raw, int):
			return raw
		else:
			return decode_id(raw)



class Named(MCBaseClass):
	name: str=Field(frozen=True)
	


class NamedIdItem(IdItem, Named):
	...


class NamedTokenItem(TokenItem, Named):
	...


class RuledEntity(MCBaseClass):
	rules: list[ActionRule]=cast(list[ActionRule], Field(
		default_factory=list, frozen=False
	))
	viewsecuritylevel: Optional[int]=Field(default=0, frozen=False)