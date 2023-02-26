from typing import (Any, Optional, Iterable, Iterator)
from dataclasses import dataclass
from .user_role_def import UserRoleDomain

@dataclass()
class ActionRule:
	name: str=""
	span: int=0
	count: int=0
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