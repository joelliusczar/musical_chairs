from typing import Any, Mapping
from .lost_found import Lost

class DictDotMap:
	@staticmethod
	def get(d: dict[str, Any], path: str, default: Any=Lost()) -> Any:
		current = d
		for segment in path.split("."):
			if segment not in current:
				if default == Lost():
					raise KeyError(f"{path} not found")
				return default
			current = current[segment]
		return current


	@staticmethod
	def set(d: dict[str, Any], path: str, value: Any):
		current = d
		segments = path.split(".")
		for i in range(len(segments)):
			if i == len(segments) -1:
				current[segments[i]] = value
			elif segments[i] not in current:
				current[segments[i]] = {}
			current = current[segments[i]]
			

	@staticmethod
	def set_many(
		d: dict[str, Any],
		paths: Mapping[str, Any],
		omitNulls: bool = False
	):
		for k, v in paths.items():
			if omitNulls and v == None:
				continue
			DictDotMap.set(d, k, v)

	@staticmethod
	def unflatten(
		paths: Mapping[str, Any],
		omitNulls: bool = False
	) -> dict[str, Any]:
		result: dict[str, Any] = {}
		DictDotMap.set_many(result, paths, omitNulls)
		return result
