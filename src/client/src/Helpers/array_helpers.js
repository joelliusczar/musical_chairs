export const buildArrayQueryStr = (arr, key) => {
	const queryObj = new URLSearchParams();
	for(const item of arr) {
		queryObj.append(key, item);
	}
	return `?${queryObj.toString()}`;
};