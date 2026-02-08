
from pathlib import Path
from typing import Any, cast, Iterator

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
	dictB: dict[Any, Any],
	exclude: set[str] | None = None
) -> list[str]:
	if not exclude:
		exclude = set()
	mismatchs: list[str] = []
	for k,v in dictA.items():
		if k not in dictB:
			if k in exclude:
				continue
			mismatchs.append(k)
			continue
		if type(v) == dict:
			if type(dictB[k]) != dict:
				if k in exclude:
					continue
				mismatchs.append(k)
				continue

			mismatchs.extend(f"{k}.{m}" for m in \
				mismatched_properties(
					cast(dict[Any, Any], v), 
					dictB[k],
					{x.removeprefix(f"{k}.") for x in exclude}
				)
			)
			continue
		if type(v) == list:
			if type(dictB[k]) != list:
				if k in exclude:
					continue
				mismatchs.append(k)
				continue
			mismatchs.extend(
				mismatched_list(
					k,
					cast(list[Any],v),
					dictB[k],
					exclude
				)
			)
			continue
		if v != dictB[k]:
			if k in exclude:
				continue
			mismatchs.append(k)
			continue
	return mismatchs


def mismatched_list(
	key: str,
	listA: list[Any],
	listB: list[Any],
	exclude: set[str]
) -> Iterator[str]:
	if len(listA) != len(listB):
		yield key
		return
	for idx, item in enumerate(listA):
		if type(item) == dict:
			if type(listB[idx]) != dict:
				yield f"{key}[{idx}]"
				continue
			yield from (
				f"{key}[{idx}].{m}" for m in mismatched_properties(
					cast(dict[Any, Any], item), 
					listB[idx],
					{x.removeprefix(f"{key}[].") for x in exclude}
				)
			)
			continue
		if type(item) == list:
			if type(listB[idx]) != list:
				yield from f"{key}[{idx}]"
			yield from (mismatched_list(
				key,
				cast(list[Any],item),
				listB[idx],
				exclude
			))
			continue
		if item != listB[idx]:
			yield f"{key}[{idx}]"
		




def get_sentences():
	s = Path("mocks/absalomabsalom.txt").read_text()
	sentences = s.replace("\n","").split(".")
	return sentences
