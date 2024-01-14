import sys
from typing import (Any, Optional, Iterable, Iterator, Callable)
from .generic_dtos import MCBaseClass
from .user_role_def import UserRoleDomain, RulePriorityLevel
from itertools import groupby, chain
from operator import attrgetter





class ActionRule(MCBaseClass):
	name: str=""
	span: float=0
	count: float=0
	#if priority is not specified, priority should be specific
	# (station, path) > general
	priority: Optional[int]=RulePriorityLevel.NONE.value
	domain: str=UserRoleDomain.Site.value
	# model_config=ConfigDict(revalidate_instances="subclass-instances")

	@staticmethod
	def sorted(rules: Iterable["ActionRule"]) -> list["ActionRule"]:
		s = sorted(rules, key=attrgetter("score"))
		s.sort(key=attrgetter("priority"), reverse=True)
		s.sort(key=attrgetter("name"))
		return s

	@staticmethod
	def aggregate(
		*args: Iterable["ActionRule"],
		filter: Callable[["ActionRule"], bool]=lambda r: True
	) -> list["ActionRule"]:
		return ActionRule.sorted(r for r in chain(
			*args
		) if filter(r))

	@property
	def priorityElse(self) -> int:
		return self.priority or RulePriorityLevel.NONE.value

	@property
	def score(self) -> float:
		if self.noLimit:
			return sys.maxsize
		return abs(self.count / self.span)

	@property
	def noLimit(self) -> bool:
		return not self.span

	@property
	def blocked(self) -> bool:
		#noLimit has higher precedence because I don't want to rewrite
		#my comparison methods again
		return not self.noLimit and not self.count

	def conforms(self, rule: str) -> bool:
		return rule == self.name

	def __gt__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		return self.score > other.score

	def __lt__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		return self.score < other.score

	def __ge__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		return self.score >= other.score

	def __le__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		return self.score <= other.score

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.name == other.name and\
			self.span == other.span and self.count == other.count

	def __ne__(self, other: Any) -> bool:
		if not other:
			return True
		return self.name != other.name or\
			self.span != other.span or self.count != other.count

	def __hash__(self) -> int:
		return hash((
			self.name,
			self.span,
			self.count,
			self.priority
		))

	def to_path_rule(self, path: str) -> "PathsActionRule":
		return PathsActionRule(
			name=self.name,
			span=self.span,
			count=self.count,
			priority=self.priority,
			domain=self.domain,
			path=path
		)

	@staticmethod
	def filter_out_repeat_roles(
		rules: Iterable["ActionRule"]
	) -> Iterator["ActionRule"]:
		yield from (next(g[1]) for g in groupby(rules, key=lambda k: k.name))


class StationActionRule(ActionRule):
	domain: str=UserRoleDomain.Station.value


class PathsActionRule(ActionRule):
	path: Optional[str]=None
	domain: str=UserRoleDomain.Path.value

	def is_parent_path(self, path: Optional[str]) -> bool:
		if not self.path or not path:
			return False
		return path.startswith(self.path) and len(path) > len(self.path)

	def __eq__(self, __value: Any) -> bool:
		if self.path is None and not hasattr(__value, "path"):
			return super().__eq__(__value)
		return super().__eq__(__value) \
			and self.path == __value.path

	def __hash__(self) -> int:
		if self.path is None:
			return super().__hash__()
		return hash((
			self.name,
			self.span,
			self.count,
			self.priority,
			self.domain,
			self.path
		))

	def __ne__(self, other: Any) -> bool:
		return super().__ne__(other) \
			or self.path != other.path

	def __gt__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		if isinstance(other, type(self)):
			if self.is_parent_path(other.path):
				return False
			if other.is_parent_path(self.path):
				return True
		else:
			return True
		return self.score > other.score

	def __lt__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		if isinstance(other, type(self)):
			if self.is_parent_path(other.path):
				return True
			if other.is_parent_path(self.path):
				return False
		else:
			return False
		return self.score < other.score

	def __le__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		if isinstance(other, type(self)):
			if self.is_parent_path(other.path):
				return True
			if other.is_parent_path(self.path):
				return False
		else:
			return False
		return self.score <= other.score

	def __ge__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		if isinstance(other, type(self)):
			if self.is_parent_path(other.path):
				return False
			if other.is_parent_path(self.path):
				return True
		else:
			return True
		return self.score >= other.score


action_rule_class_map = {
	UserRoleDomain.Path.value: PathsActionRule,
	UserRoleDomain.Station.value: StationActionRule,
	UserRoleDomain.Site.value: ActionRule
}