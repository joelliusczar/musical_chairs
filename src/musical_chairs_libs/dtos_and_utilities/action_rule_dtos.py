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
from .user_role_def import RulePriorityLevel
from .constants import UserRoleSphere
from itertools import groupby, chain
from operator import attrgetter
from sqlalchemy.engine.row import RowMapping
from .user_role_def import RulePriorityLevel



@dataclass
class ActionRule:
	name: str
	span: float=0 #this should be total seconds
	quota: float=0
	#if priority is not specified, priority should be specific
	# (station, path) > general
	priority: Optional[int]=RulePriorityLevel.NONE.value
	sphere: str=UserRoleSphere.Site.value
	keypath: Optional[str]=None
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
		return abs(self.quota / self.span)


	@property
	def noLimit(self) -> bool:
		return not self.span


	@property
	def blocked(self) -> bool:
		#noLimit has higher precedence because I don't want to rewrite
		#my comparison methods again
		return not self.noLimit and not self.quota


	def conforms(self, rule: str) -> bool:
		return rule == self.name


	def __gt__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if self.sphere > other.sphere:
			return True
		if self.sphere < other.sphere:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		if all(d == UserRoleSphere.Path.value for d in (self.sphere, other.sphere)):
			if self.is_parent_path(other.keypath):
				return False
			if other.is_parent_path(self.keypath):
				return True
		else:
			if (self.keypath or "\0") > (other.keypath or "\0"):
				return True
			if (self.keypath or "\0") < (other.keypath or "\0"):
				return False
		return self.score > other.score


	def __lt__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if self.sphere < other.sphere:
			return True
		if self.sphere > other.sphere:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		if all(d == UserRoleSphere.Path.value for d in (self.sphere, other.sphere)):
			if self.is_parent_path(other.keypath):
				return True
			if other.is_parent_path(self.keypath):
				return False
		else:
			if (self.keypath or "\0") < (other.keypath or "\0"):
				return True
			if (self.keypath or "\0") > (other.keypath or "\0"):
				return False
		return self.score < other.score


	def __ge__(self, other: "ActionRule") -> bool:
		if self.name > other.name:
			return True
		if self.name < other.name:
			return False
		if self.sphere > other.sphere:
			return True
		if self.sphere < other.sphere:
			return False
		if (self.priorityElse) > (other.priorityElse):
			return True
		if (self.priorityElse) < (other.priorityElse):
			return False
		if all(d == UserRoleSphere.Path.value for d in (self.sphere, other.sphere)):
			if self.is_parent_path(other.keypath):
				return False
			if other.is_parent_path(self.keypath):
				return True
		else:
			if (self.keypath or "\0") > (other.keypath or "\0"):
				return True
			if (self.keypath or "\0") < (other.keypath or "\0"):
				return False
		return self.score >= other.score


	def __le__(self, other: "ActionRule") -> bool:
		if self.name < other.name:
			return True
		if self.name > other.name:
			return False
		if self.sphere < other.sphere:
			return True
		if self.sphere > other.sphere:
			return False
		if (self.priorityElse) < (other.priorityElse):
			return True
		if (self.priorityElse) > (other.priorityElse):
			return False
		if all(d == UserRoleSphere.Path.value for d in (self.sphere, other.sphere)):
			if self.is_parent_path(other.keypath):
				return True
			if other.is_parent_path(self.keypath):
				return False
		else:
			if (self.keypath or "\0") < (other.keypath or "\0"):
				return True
			if (self.keypath or "\0") > (other.keypath or "\0"):
				return False
		return self.score <= other.score


	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.name == other.name\
			and self.span == other.span\
			and self.quota == other.quota\
			and self.sphere == other.sphere\
			and self.keypath == other.keypath


	def __ne__(self, other: Any) -> bool:
		if not other:
			return True
		return self.name != other.name \
			or self.span != other.span\
			or self.quota != other.quota\
			or self.sphere != other.sphere\
			or self.keypath != other.keypath


	def __hash__(self) -> int:
		return hash((
			self.name,
			self.span,
			self.quota,
			self.priority,
			self.sphere,
			self.keypath
		))



	@staticmethod
	def filter_out_repeat_roles(
		rules: Iterable["ActionRule"]
	) -> Iterator["ActionRule"]:
		yield from (next(g[1]) for g in groupby(rules, key=lambda k: k.name))


	@staticmethod
	def row_to_action_rule(row: RowMapping) -> "ActionRule":

		return ActionRule(
			name=row["rule>name"],
			span=row["rule>span"],
			quota=row["rule>quota"],
			#if priortity is explict use that
			#otherwise, prefer station specific rule vs non station specific rule
			priority=cast(int,row["rule>priority"]) if row["rule>priority"] \
				else RulePriorityLevel.INVITED_USER.value,
			sphere=row["rule>sphere"]
		)


	def is_parent_path(self, path: Optional[str]) -> bool:
		if not self.keypath or not path:
			return False
		return path.startswith(self.keypath) and len(path) > len(self.keypath)