import { IdType } from "./generic_types";

export interface ListData<T> {
	items: T[]
}

export interface TableData<T> extends ListData<T> {
	totalRows: number
}

export interface PageableParams {
	searchTerm?: string
	page?: number | null
	pageSize?: number
	rows?: number | null
	id?: IdType
	name?: string
	limit?: number
}