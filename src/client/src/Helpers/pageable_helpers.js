export const urlBuilderFactory = (routeFn) => {
	return (params, currentLocation) => {
		const queryObj = new URLSearchParams(currentLocation);
		if(params.page) {
			queryObj.set("page", params.page);
		}
		if(params.rows) {
			queryObj.set("rows", params.rows);
		}
		if(params.id) {
			queryObj.set("id", params.id);
		}
		if(params.name) {
			queryObj.set("name", params.name);
		}
		else if (params.name === "") {
			queryObj.delete("name");
		}
		const queryStr = `?${queryObj.toString()}`;
		return `${routeFn(params)}${queryStr}`;
	};
};

export const getRowsCount = (currentLocation) => {
	const queryObj = new URLSearchParams(currentLocation);
	return parseInt(queryObj.get("rows") || "50");
};

export const getPageCount = (currentLocation, totalRows) => {
	const queryObj = new URLSearchParams(currentLocation);
	const rows = parseInt(queryObj.get("rows") || "50");
	if(rows < 1) {
		return 0;
	}
	return Math.floor(totalRows / rows);
};