from typing import (
	List,
	TypeVar,
	Generic,
	Optional,
	cast,
)
from pydantic import BaseModel as MCBaseClass, ConfigDict, Field
from .action_rule_dtos import ActionRule


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

class FrozenNamed(FrozenBaseClass):
	name: str

class FrozenNamedIdItem(FrozenIdItem, FrozenNamed):
	...


class IdItem(MCBaseClass):
	id: int=Field(frozen=True)

class Named(MCBaseClass):
	name: str=Field(frozen=True)

class NamedIdItem(IdItem, Named):
	...


class RuledEntity(MCBaseClass):
	rules: list[ActionRule]=cast(list[ActionRule], Field(
		default_factory=list, frozen=False
	))
	viewsecuritylevel: Optional[int]=Field(default=0, frozen=False)