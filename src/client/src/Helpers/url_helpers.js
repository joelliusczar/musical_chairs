export const buildArrayQueryStr = (arr, key) => {
	const queryObj = new URLSearchParams();
	for (const item of arr) {
		queryObj.append(key, item);
	}
	return `?${queryObj.toString()}`;
};

export const buildArrayQueryStrFromObj = (obj) => {
	const queryObj = new URLSearchParams();
	for (const key of Object.keys(obj)) {
		const value = obj[key];
		if (Array.isArray(value)) {
			for (const item of value) {
				queryObj.append(key, item);
			}
			continue;
		}
		if (typeof value === "string" || typeof value === "number") {
			queryObj.append(key, value);
		}
	}
};