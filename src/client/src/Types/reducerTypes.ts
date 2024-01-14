import { KeyValue } from "./generic_types";



export enum WaitingTypes {
	started = "started",
	restart = "restart",
	done = "done",
	failed = "failed",
	set = "reset",
	run = "run",
	update = "update",
	add = "add", //implemented as needed
	updateItem = "updateItem", //implemented as needed
	remove = "remove", //implemented as needed
	assign = "assign", //implemented as needed
}


export interface VoidStoreShape {
	key?: KeyValue,
	callStatus: string | null,
	error: string | null,
}

export interface SimpleStoreShape<T> extends VoidStoreShape {
	data: T
}

export interface KeyedStoreShape<StoreType> {
	[key: KeyValue]: StoreType
}

export interface ListDataShape<T> {
	items: T[],
}

export interface PageableListDataShape<T>
	extends ListDataShape<T>
{
		totalrows: number
}

export type ListStoreShape<DataShape> =
	SimpleStoreShape<ListDataShape<DataShape>>;
export type PageableListStoreShape<T> =
	SimpleStoreShape<PageableListDataShape<T>>;



