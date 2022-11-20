from typing import Any


def normalize_dict(targetDict: dict[Any, Any]) -> dict[Any, Any]:
	for k,v in targetDict.items():
		if type(v) == list and k != "touched":
			targetDict[k] = sorted(v, key=lambda k: k["id"])
		if type(v) == dict:
			targetDict[k] =  normalize_dict(v)
	return targetDict

def mismatched_properties(
	dictA: dict[Any, Any],
	dictB: dict[Any, Any]
) -> list[str]:
	mismatchs: list[str] = []
	for k,v in dictA.items():
		if k not in dictB:
			mismatchs.append(k)
			continue
		if type(v) == dict:
			if type(dictB[k]) != dict:
				mismatchs.append(k)
				continue
			mismatchs.extend(f"{k}.{m}" for m in mismatched_properties(v, dictB[k]))
			continue
		if v != dictB[k]:
			mismatchs.append(k)
			continue
	return mismatchs