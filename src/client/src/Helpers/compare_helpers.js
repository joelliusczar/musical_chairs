export const userKeyMatch = (key, owner) => {
	if( typeof key === "number") {
		return key === owner?.id;
	}
	else if (typeof key === "string") {
		return key === owner?.username;
	}
	return false;
};

export const keyMatch = (key, owner) => {
	if( typeof key === "number") {
		return key === owner?.id;
	}
	else if (typeof key === "string") {
		return key === owner?.name;
	}
	return false;
};