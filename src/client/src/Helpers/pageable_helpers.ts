import { PrimitiveObject } from "../Types/generic_types";
import { PageableParams } from "../Types/pageable_types";

export class UrlBuilder<T extends PageableParams> {
	routeFn: (routeParams: T) => string;
	getOtherUrl: (params: T, currentLocation: string) => string;
	getThisUrl: (
		params: PageableParams,
		currentLocation: string,
		currentPathName: string
	) => string;

	constructor(routeFn: (routeParams: T) => string) {
		this.routeFn = routeFn;
		this.getOtherUrl = this.__getOtherUrl__.bind(this);
		this.getThisUrl = this.__getThisUrl__.bind(this);
	}

	private __buildQueryString__(
		params: PageableParams,
		currentLocation: string
	): string
	{
		const sortKey = "sortdir";
		const queryObj = new URLSearchParams(currentLocation);
		const dontDelete = ["page", "limit", "id", "orderby", sortKey];
		//loop throuh keys in the params
		Object.keys(params).forEach((key) => {
			//if present, replace
			if (key === "orderby") {
				const sortDir = queryObj.get(sortKey);
				if (sortDir === "asc") {
					queryObj.set(sortKey, "dsc");
				}
				else if (sortDir === "dsc") {
					queryObj.delete(sortKey);
				}
				else {
					queryObj.set(sortKey, "asc");
				}
			}
			if (params[key]) {
				queryObj.set(key, params[key] as string);
			}
			//if key is not in params and not one of the dontDelete, delete it
			else if (! dontDelete.some(k => k === key)) {
				if (params[key] === "") {
					queryObj.delete(key);
				}
			}
		});
		const queryStr = `?${queryObj.toString()}`;
		return queryStr;
	}

	private __getOtherUrl__(params: T, currentLocation: string): string {
		const queryStr = this.__buildQueryString__(params, currentLocation);
		return `${this.routeFn(params)}${queryStr}`;
	}

	private __getThisUrl__(
		params: PageableParams,
		currentLocation: string,
		currentPathName: string
	): string
	{
		const queryStr = this.__buildQueryString__(params, currentLocation);
		return `${currentPathName}${queryStr}`;
	}
}

export const getRowsCount = (currentLocation: string) => {
	const queryObj = new URLSearchParams(currentLocation);
	return parseInt(queryObj.get("limit") || "50");
};

export const getPageCount = (currentLocation: string, totalRows: number) => {
	const queryObj = new URLSearchParams(currentLocation);
	const rows = parseInt(queryObj.get("limit") || "50");
	if(rows < 1) {
		return 0;
	}
	return Math.ceil(totalRows / rows);
};

export const getSearchParams = (currentLocation: string) => {
	const queryObj = new URLSearchParams(currentLocation);
	const searchTerms: PrimitiveObject = {};
	for (const [key, value] of queryObj) {
		if (key === "page") {
			searchTerms[key] = parseInt(value || "1");
		}
		else if (key === "rows") {
			searchTerms[key] = parseInt(value || "50");
		}
		else {
			searchTerms[key] = value;
		}
	}
	return searchTerms;
};