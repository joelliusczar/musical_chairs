import { KeyType } from "../../Types/generic_types";



export enum WaitingTypes {
	started = "started",
	restart = "restart",
	done = "done",
	failed = "failed",
	reset = "reset",
	read = "read",
	add = "add", //implemented as needed
	updateItem = "updateItem", //implemented as needed
	remove = "remove", //implemented as needed
	assign = "assign", //implemented as needed
}

export type ActionPayload<T, U=T> = {
	type: WaitingTypes.started,
	payload?: unknown
} |  {
	type: WaitingTypes.restart,
	payload?: unknown
} |  {
	type: WaitingTypes.done,
	payload?: T
} | {
	type: WaitingTypes.failed,
	payload: string
} | {
	type: WaitingTypes.reset,
	payload: T
} | {
	type: WaitingTypes.read,
	payload: ((state: T) => void)
} | {
	type: WaitingTypes.assign,
	payload: Partial<T>
} | {
	type: WaitingTypes.add,
	payload: U
} | {
	type: WaitingTypes.updateItem,
	payload: KeyAndDataOrUpdater<U>
} | {
	type: WaitingTypes.remove,
	payload: {
		key: KeyType,
	}
}

export type ListActionPayload<T> = ActionPayload<ListDataShape<T>, T>

export interface KeyAndData<T> {
	key: KeyType,
	data: T,
}

export type DataOrUpdater<T> =
	T | ((data: T) => T);

export interface KeyAndDataOrUpdater<T> {
	key: KeyType,
	dataOrUpdater: DataOrUpdater<T>,
}

export interface Dispatches {
	started(): {
		type: WaitingTypes.started,
	},
	started<T>(payload: T): {
		type: WaitingTypes.started,
		payload: T
	},
	restart: (payload?: unknown) => {
		type: WaitingTypes.restart,
		payload?: unknown
	},
	done<T>(payload: T):{
		type: WaitingTypes.done,
		payload: T
	},
	done(): {
		type: WaitingTypes.done
	},
	done<T>(payload?: T):{
		type: WaitingTypes.done,
		payload?: T
},
	failed: <T extends string | KeyAndData<string>>(payload: T) => {
		type: WaitingTypes.failed,
		payload: T extends string ? string : KeyAndData<string>
	},
	reset: <T>(payload: T) => {
		type: WaitingTypes.reset,
		payload: T
	},
	add: <T>(payload: T) => {
		type: WaitingTypes.add,
		payload: T
	},
	update: <T, U extends DataOrUpdater<T>>(
		key: KeyType,
		payload: U
	) => {
		type: WaitingTypes.updateItem,
		payload: {
			key: KeyType,
			dataOrUpdater: U,
		}
	},
	remove: (key: KeyType) => {
		type: WaitingTypes.remove,
		payload: {
			key: KeyType,
		},
	},
	assign: <T>(payload: T) => {
		type: WaitingTypes.assign,
		payload: Partial<T>
	},
	read: <T>(fn: (data: T) => void) => {
		type: WaitingTypes.read,
		payload: (data: T) => void
	},
}


export interface VoidStoreShape {
	callStatus: string | null,
	error: string | null,
}

export interface SimpleStoreShape<T> extends VoidStoreShape {
	data: T
}

export interface KeyedStoreShape<StoreType> {
	[key: KeyType]: StoreType
}

export interface ListDataShape<T> {
	items: T[],
}

export interface PageableListDataShape<T>
	extends ListDataShape<T>
{
		totalRows: number
}

export type ListStoreShape<DataShape> =
	SimpleStoreShape<ListDataShape<DataShape>>;
export type PageableListStoreShape<T> =
	SimpleStoreShape<PageableListDataShape<T>>;



export type ReducerPaths<T, StoreType=SimpleStoreShape<T>, U=T> =
	{
	[key in WaitingTypes.started | WaitingTypes.restart]: (
		state: StoreType
	) => StoreType
	} &
	{
		[key in WaitingTypes.done]: (
			state: StoreType,
			payload?: T
		) => StoreType
	} &
	{
		[key in WaitingTypes.failed]: (
			state: StoreType,
			payload: string
		) => StoreType
	} &
	{
		[key in WaitingTypes.reset]: (
			state: StoreType,
			payload: T
		) => StoreType
	} &
	{
		[key in WaitingTypes.read]: (
			state: StoreType,
			payload: ((state: T) => void)
		) => StoreType
	} &
	{
		[key in WaitingTypes.assign]: (
			state: StoreType,
			payload: Partial<T>
		) => StoreType
	} &
	{
	[key in WaitingTypes.add]?: (
			state: StoreType,
			payload: U
		) => StoreType
	} &
	{
		[key in WaitingTypes.updateItem]?: (
			state: StoreType,
			payload: {
				key: KeyType,
				dataOrUpdater: DataOrUpdater<U>
			}
		) => StoreType
	} &
	{
		[key in WaitingTypes.remove]?: (
			state: StoreType,
			payload: {
				key: string,
			}
		) => StoreType
	};


export type MiddlewareFn<ActionPayloadType, StoreType> = (
	accumulation: StoreType,
	state: StoreType,
	action: ActionPayloadType
) => StoreType;


export type AnonReducer<StoreType> =
	(state: StoreType, payload: unknown) => StoreType;