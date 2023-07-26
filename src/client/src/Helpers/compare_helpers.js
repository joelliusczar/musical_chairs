export const userKeyMatch = (key, owner) => {
	if (key === owner?.id?.toString()) {
		return true;
	}
	if (key === owner?.username) {
		return true;
	}
	return false;
};

export const keyMatch = (key, object) => {
	if (key === object?.id?.toString()) {
		return true;
	}
	if (key === object?.name) {
		return true;
	}
	return false;
};