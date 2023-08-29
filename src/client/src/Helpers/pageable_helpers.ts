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
		const queryObj = new URLSearchParams(currentLocation);
		if(params.page) {
			queryObj.set("page", params.page as unknown as string);
		}
		if(params.rows) {
			queryObj.set("rows", params.rows as unknown as string);
		}
		if(params.id) {
			queryObj.set("id", params.id as unknown as string);
		}
		if(params.name) {
			queryObj.set("name", params.name);
		}
		else if (params.name === "") {
			queryObj.delete("name");
		}
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
	return parseInt(queryObj.get("rows") || "50");
};

export const getPageCount = (currentLocation: string, totalRows: number) => {
	const queryObj = new URLSearchParams(currentLocation);
	const rows = parseInt(queryObj.get("rows") || "50");
	if(rows < 1) {
		return 0;
	}
	return Math.floor(totalRows / rows);
};