import { IdValue, PrimitiveObject } from "./generic_types";

export interface ListData<T> {
	items: T[]
}

export interface TableData<T> extends ListData<T> {
	totalrows: number
}

export type PageableParams = PrimitiveObject & {
	searchTerm?: string
	page?: number | null
	pageSize?: number
	rows?: number | null
	id?: IdValue
	name?: string
	limit?: number
}