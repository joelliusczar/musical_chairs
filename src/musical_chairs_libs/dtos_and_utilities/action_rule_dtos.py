import sys
from dataclasses import dataclass
from typing import (
	Any, 
	Optional, 
	Iterable, 
	Iterator, 
	Callable,
	cast
)
from .user_role_def import UserRoleDomain, RulePriorityLevel
from itertools import groupby, chain
from operator import attrgetter
from sqlalchemy.engine.row import RowMapping
from .user_role_def import RulePriorityLevel



@dataclass
class ActionRule:
	name: str=""
	span: float=0 #this should be total seconds
	count: float=0
	#if priority is not specified, priority should be specific
	# (station, path) > general
	priority: Optional[int]=RulePriorityLevel.NONE.value
	domain: str=UserRoleDomain.Site.value
	path: Optional[str]=None
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
		if self.domain > other.domain:
			return True
		if self.domain < other.domain:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		if all(d == UserRoleDomain.Path.value for d in (self.domain, other.domain)):
			if self.is_parent_path(other.path):
				return False
			if other.is_parent_path(self.path):
				return True
		else:
			if (self.path or "\0") > (other.path or "\0"):
				return True
			if (self.path or "\0") < (other.path or "\0"):
				return False
		return self.score > other.score


	def __lt__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if self.domain < other.domain:
			return True
		if self.domain > other.domain:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		if all(d == UserRoleDomain.Path.value for d in (self.domain, other.domain)):
			if self.is_parent_path(other.path):
				return True
			if other.is_parent_path(self.path):
				return False
		else:
			if (self.path or "\0") < (other.path or "\0"):
				return True
			if (self.path or "\0") > (other.path or "\0"):
				return False
		return self.score < other.score


	def __ge__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if self.domain > other.domain:
			return True
		if self.domain < other.domain:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		if all(d == UserRoleDomain.Path.value for d in (self.domain, other.domain)):
			if self.is_parent_path(other.path):
				return False
			if other.is_parent_path(self.path):
				return True
		else:
			if (self.path or "\0") > (other.path or "\0"):
				return True
			if (self.path or "\0") < (other.path or "\0"):
				return False
		return self.score >= other.score


	def __le__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if self.domain < other.domain:
			return True
		if self.domain > other.domain:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		if all(d == UserRoleDomain.Path.value for d in (self.domain, other.domain)):
			if self.is_parent_path(other.path):
				return True
			if other.is_parent_path(self.path):
				return False
		else:
			if (self.path or "\0") < (other.path or "\0"):
				return True
			if (self.path or "\0") > (other.path or "\0"):
				return False
		return self.score <= other.score


	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.name == other.name\
			and self.span == other.span\
			and self.count == other.count\
			and self.domain == other.domain\
			and self.path == other.path


	def __ne__(self, other: Any) -> bool:
		if not other:
			return True
		return self.name != other.name \
			or self.span != other.span\
			or self.count != other.count\
			or self.domain != other.domain\
			or self.path != other.path


	def __hash__(self) -> int:
		return hash((
			self.name,
			self.span,
			self.count,
			self.priority,
			self.domain,
			self.path
		))



	@staticmethod
	def filter_out_repeat_roles(
		rules: Iterable["ActionRule"]
	) -> Iterator["ActionRule"]:
		yield from (next(g[1]) for g in groupby(rules, key=lambda k: k.name))


	@staticmethod
	def row_to_action_rule(row: RowMapping) -> "ActionRule":

		return ActionRule(
			name=row["rule_name"],
			span=row["rule_span"],
			count=row["rule_count"],
			#if priortity is explict use that
			#otherwise, prefer station specific rule vs non station specific rule
			priority=cast(int,row["rule_priority"]) if row["rule_priority"] \
				else RulePriorityLevel.STATION_PATH.value,
			domain=row["rule_domain"]
		)


	def is_parent_path(self, path: Optional[str]) -> bool:
		if not self.path or not path:
			return False
		return path.startswith(self.path) and len(path) > len(self.path)


