from collections.abc import MutableMapping
from typing import (
	Any,
	Mapping,
	Optional,
	Iterator,
	Tuple,
	Iterable,
	MutableSet
)
from .id_dict import IdDict

class PathDict(MutableMapping[str, Any]):

	def __init__(self,
		paths: Optional[Mapping[str, Any]] = None,
		omitNulls: bool = False,
		defaultValues: Optional[Mapping[str, Any]] = None,
	) -> None:
		self.__store__: dict[str, Any] = {}
		if paths:
			for k, v in paths.items():
				if v == None:
					if defaultValues and k in defaultValues:
						self[k] = defaultValues[k]
						continue
					elif omitNulls:
						continue
				self[k] = v


	def __len__(self) -> int:
		return len(self.__store__)


	def __getitem__(self, key: str) -> Any:
		current = self.__store__
		for segment in key.split("."):
			if segment not in current:
				raise KeyError(f"{key} not found")
			current = current[segment]
		return current


	def __setitem__(self, key: str, value: Any) -> None:
		current = self.__store__
		segments = key.split(".")
		for i in range(len(segments)):
			if i == len(segments) -1:
				current[segments[i]] = value
			elif segments[i] not in current:
				current[segments[i]] = {}
			current = current[segments[i]]


	def __delitem__(self, key: str) -> None:
		current = self.__store__
		segments = key.split(".")
		parents: list[Tuple[dict[str,Any], str]] = []
		for i in range(len(segments)):
			if i == len(segments) -1:
				del current[segments[i]]
			current = current[segments[i]]
			parents.append((current, segments[i]))
		for lvl in reversed(parents):
			del lvl[0][lvl[1]]


	def __iter__(self) -> Iterator[str]:
		return iter(self.__store__)


	def __str__(self) -> str:
		return str(self.__store__)


	def __repr__(self) -> str:
		return repr(self.__store__)
	
	@staticmethod
	def prefix_merge_collect(
		dicts: Iterable["PathDict"],
		pivotKey: str,
		*prefixes: str
	) -> Iterator["PathDict"]:
		copy = None
		for d in dicts:
			if not copy:
				copy = PathDict()
			if pivotKey in copy.__store__\
				and d.__store__[pivotKey] != copy.__store__[pivotKey]\
			:
				for prefix in prefixes:
					if prefix in copy.__store__:
						copy.__store__[prefix] = list(copy.__store__[prefix])
				yield copy
				copy = PathDict()
			for k,v in d.__store__.items():
				prefix = next((p for p in prefixes if k.startswith(p)), None)
				if prefix:
					if prefix in copy.__store__:
						if not isinstance(copy.__store__[prefix], MutableSet):
							raise TypeError(
								f"Dictionary cannot be merged. {prefix} already exists "
								"and it is not a list"
							)
						copy.__store__[prefix].add(IdDict(v[pivotKey], v))
					else:
						copy.__store__[prefix] = set([IdDict(v[pivotKey], v)])
				else:
					copy[k] = v
		if copy:
			for prefix in prefixes:
				if prefix in copy.__store__:
					copy.__store__[prefix] = list(copy.__store__[prefix])
			yield copy
						
