import { KeyType, Error } from "./generic_types";



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
};

export type ActionPayloadType<T, U=T> = {
	type: WaitingTypes.started,
	payload?: unknown
} |  {
	type: WaitingTypes.restart,
	payload?: unknown
} |  {
	type: WaitingTypes.done,
	payload?: T | unknown
} | {
	type: WaitingTypes.failed,
	payload: T extends KeyAndData<any> ? KeyAndData<string> : string
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
	payload: KeyAndDataOrUpdater<T>
} | {
	type: WaitingTypes.remove,
	payload: {
		key: KeyType,
	}
};

export interface ReducerAction<DataShape> {
	type: WaitingTypes,
	payload: DataShape
};

export interface KeyAndData<DataShape> {
	key: string,
	data: DataShape,
};

	export type DataOrUpdater<DataShape> =
		DataShape | ((data: DataShape) => DataShape);

export interface KeyAndDataOrUpdater<DataShape> {
	key: KeyType,
	dataOrUpdater: DataOrUpdater<DataShape>,
}

export type BasicDispatch = <T>(payload: T) => ReducerAction<T>;

export type OptionalPayloadDispatch =
	<T>(payload?: T) => ReducerAction<T | undefined>;

export type EmptyPayloadDispatch = () => {
	type: WaitingTypes,
};

export type UpdateDispatch = <T>(
	key: KeyType,
	dataOrUpdater: T | ((data: T) => T)
) => {
	type: WaitingTypes,
	payload: {
		key: KeyType,
		dataOrUpdater: T | ((data: T) => T)
	},
};

export type KeyedDispatch = (key: KeyType) => {
	type: WaitingTypes,
	payload: {
		key: KeyType,
	},
};

export type ReadDispatch = <T>(fn: (data: T) => void) => {
	type: string,
	payload: (data: T) => void
};

export interface Dispatches {
	started: (payload?: unknown) => {
		type: WaitingTypes.started,
		payload?: unknown
	},
	restart: (payload?: unknown) => {
		type: WaitingTypes.restart,
		payload?: unknown
	},
	done: <T>(payload?: T) => {
		type: WaitingTypes.done,
		payload?: T
	},
	failed: (payload: string) => {
		type: WaitingTypes.failed,
		payload: string
	},
	reset: <T>(payload: T) => {
		type: WaitingTypes.reset,
		payload: T
	},
	add: <T>(payload: T) => {
		type: WaitingTypes.add,
		payload: T
	},
	update: <T>(key: KeyType, payload: DataOrUpdater<T>) => {
		type: WaitingTypes.updateItem,
		payload: KeyAndDataOrUpdater<T>
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
	read: ReadDispatch,
};


export interface VoidState {
	callStatus: string | null,
	error: string | null,
};

export interface SimpleStore<DataShape> extends VoidState {
	data: DataShape
};

export interface ListDataShape<DataShape> {
	items: DataShape[],
};

export interface PageableListDataShape<T>
	extends ListDataShape<T>
{
		totalRows: number
};

export type ListStore<DataShape> = SimpleStore<ListDataShape<DataShape>>;
export type PageableListStore<DataShape> =
	SimpleStore<PageableListDataShape<DataShape>>;

export interface KeyedStore<DataShape> {
	[key: string]: SimpleStore<DataShape>
}

export type AnyPayloadReducerFn<DataShape> = (
	state: SimpleStore<DataShape>,
	action: {
		type: string,
		payload: any
	}
) => SimpleStore<DataShape>;


export type ReducerMods<T, StoreType=SimpleStore<T>, U=T> =
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
			payload: T extends KeyAndData<any> ? KeyAndData<string> : string
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
				key: number | string,
				dataOrUpdater: T
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
	}



export type MiddlewareFn<T, StoreType, U=T > = (
	accumulation: StoreType,
	state: StoreType,
	action: ActionPayloadType<T, U>
) => StoreType;


export class VoidState {
	callStatus: string | null = null
	error: string | null = null
};

export class InitialState<DataShape=undefined> extends VoidState {
	data?: DataShape

	constructor(data?: DataShape) {
		super();
		this.data = data
	}
};

export class RequiredDataState<DataShape> extends InitialState<DataShape> {
	data: DataShape

	constructor(data: DataShape) {
		super(data);
		this.data = data;
	}
};