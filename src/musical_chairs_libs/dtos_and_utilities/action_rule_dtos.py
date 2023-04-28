from typing import (Any, Optional, Iterable, Iterator)
from dataclasses import dataclass, field
from .user_role_def import UserRoleDomain




#We can't hash this class because it would interfere with best_rules_generator


@dataclass()
class ActionRule:
	name: str=""
	span: int=0
	count: int=0
	#if priority is not specified, priority should be specific
	# (station, path) > general
	priority: Optional[int]=0
	id: Optional[int]=None
	domain: UserRoleDomain=UserRoleDomain.Site

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
		if self.noLimit and other.noLimit:
			return False
		if self.noLimit:
			return True
		if other.noLimit:
			return False
		return abs(self.count / self.span) > (other.count / other.span)

	def __lt__(self, other: "ActionRule") -> bool:
		if self.noLimit and other.noLimit:
			return False
		if self.noLimit:
			return False
		if other.noLimit:
			return True
		return abs(self.count / self.span) < (other.count / other.span)

	def __ge__(self, other: "ActionRule") -> bool:
		if self.noLimit and other.noLimit:
			return True
		if self.noLimit:
			return True
		if other.noLimit:
			return False
		return abs(self.count / self.span) >= (other.count / other.span)

	def __le__(self, other: "ActionRule") -> bool:
		if self.noLimit and other.noLimit:
			return True
		if self.noLimit:
			return False
		if other.noLimit:
			return True
		return abs(self.count / self.span) <= (other.count / other.span)

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

	@staticmethod
	def best_rules_generator(
		records: Iterable["ActionRule"]
	) -> Iterator["ActionRule"]:
		selectedRule = None
		for rule in records:
			if not selectedRule:
				selectedRule = rule
			elif rule.name != selectedRule.name:
				yield selectedRule
				selectedRule = rule
			if (rule.priority or 0) > (selectedRule.priority or 0):
				selectedRule = rule
			#prefer the more restrictive rule
			elif rule < selectedRule:
				selectedRule = rule
		if selectedRule:
			yield selectedRule


@dataclass(frozen=True)
class PathPrefixInfo:
	path: str
	rules: list[ActionRule]=field(default_factory=list)

@dataclass()
class PathsActionRule(ActionRule):
	paths: list[str]=field(default_factory=list)

	@staticmethod
	def paths_to_rules(
		pathRules: Iterable[PathPrefixInfo]
	) -> Iterator["PathsActionRule"]:
		paths2Rules: dict[str, PathsActionRule] = {}
		for r in ((p.path, rl) for p in pathRules for rl in p.rules):
			pathRule = paths2Rules.get(r[1].name, PathsActionRule(r[1].name))
			pathRule.paths.append(r[0])
			paths2Rules[r[1].name] = pathRule
		yield from (r for r in paths2Rules.values())

	@staticmethod
	def rules_to_paths(
		rules: Iterable["PathsActionRule"]
	) -> Iterator[PathPrefixInfo]:
		pathsInfoDict: dict[str, PathPrefixInfo] = {}
		for i in ((p, r) for r in rules for p in r.paths):
			pathInfo = pathsInfoDict.get(i[0], PathPrefixInfo(i[0], []))
			pathInfo.rules.append(i[1])
			pathsInfoDict[i[0]] = pathInfo
		yield from (r for r in pathsInfoDict.values())

