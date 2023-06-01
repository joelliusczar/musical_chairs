from pathlib import Path
from typing import Any, cast

ignored_lists = {"touched", "rules"}

def normalize_dict(targetDict: dict[Any, Any]) -> dict[Any, Any]:
	for k,v in targetDict.items():
		if type(v) == list:
			if k not in ignored_lists:
				targetDict[k] = sorted(cast(list[Any], v), key=lambda k: k["id"])
		elif type(v) == dict:
			targetDict[k] =  normalize_dict(cast(dict[Any, Any], v))
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

			mismatchs.extend(f"{k}.{m}" for m in \
				mismatched_properties(cast(dict[Any, Any], v), dictB[k])
			)
			continue
		if v != dictB[k]:
			mismatchs.append(k)
			continue
	return mismatchs


def get_sentences():
	s = Path("mocks/absalomabsalom.txt").read_text()
	sentences = s.replace("\n","").split(".")
	return sentences
