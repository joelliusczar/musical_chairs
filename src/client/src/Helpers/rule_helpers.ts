import { UserRoleDef } from "../constants";
import { ActionRule } from "../Types/user_types";

export const conformsToRule = (candidate: ActionRule, basis: string) => {
	return candidate?.name?.startsWith(basis);
};

export const anyConformsToRule = (
	candidates: ActionRule[],
	basis: string
) => {
	return candidates?.some(r => conformsToRule(r, basis));
};

export const anyConformsToAnyRule = (
	candidates: ActionRule[],
	bases: string[]
) => {
	if (!bases) return true;
	if (anyConformsToRule(candidates, UserRoleDef.ADMIN)) {
		return true;
	}
	for (const rule of bases) {
		if (anyConformsToRule(candidates, rule)) {
			return true;
		}
	}
	return false;
};