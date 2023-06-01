export const conformsToRule = (candidate, basis) => {
	return candidate?.name?.startsWith(basis);
};

export const anyConformsToRule = (candidates, basis) => {
	return candidates?.some(r => conformsToRule(r, basis));
};

export const anyConformsToAnyRule = (candidates, bases) => {
	if (!bases) return true;
	for (const rule of bases) {
		if (anyConformsToRule(candidates, rule)) {
			return true;
		}
	}
	return false;
};