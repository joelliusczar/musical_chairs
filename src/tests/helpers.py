from typing import Any


def normalize_dict(targetDict: dict[Any, Any]) -> dict[Any, Any]:
	for k,v in targetDict.items():
		if type(v) == list:
			targetDict[k] = sorted(v, key=lambda k: k["id"])
		if type(v) == dict:
			targetDict[k] =  normalize_dict(v)
	return targetDict