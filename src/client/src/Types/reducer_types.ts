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
	key: string,
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
	started: OptionalPayloadDispatch,
	restart: EmptyPayloadDispatch,
	done: OptionalPayloadDispatch,
	failed: BasicDispatch,
	reset: BasicDispatch,
	add: BasicDispatch,
	update: UpdateDispatch,
	remove: KeyedDispatch,
	assign: BasicDispatch,
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

export interface PageableListDataShape<DataShape>
	extends ListDataShape<DataShape>
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



export type ReducerMods<DataShape, StoreType = SimpleStore<DataShape>> =
	{
	[key in "started" | "restart"]: (
		state: StoreType,
		payload: DataShape
	) => StoreType
	} &
	{
		[key in "done"]: (
			state: StoreType,
			payload: DataShape
		) => StoreType
	} &
	{
		[key in "failed"]: (
			state: StoreType,
			payload: DataShape extends KeyAndData<any> ? KeyAndData<string> : string
		) => StoreType
	} &
	{
		[key in "reset"]: (
			state: StoreType,
			payload: DataShape
		) => StoreType
	} &
	{
		[key in "read"]: (
			state: StoreType,
			payload: ((state: DataShape) => void)
		) => StoreType
	} &
	{
		[key in "assign"]: (
			state: StoreType,
			payload: Partial<DataShape>
		) => StoreType
	} &
	{
	[key in "add"]?: (
			state: StoreType,
			payload: any
		) => StoreType
	} &
	{
		[key in "updateItem"]?: (
			state: StoreType,
			payload: {
				key: number | string,
				dataOrUpdater: DataShape
			}
		) => StoreType
	} &
	{
		[key in "remove"]?: (
			state: StoreType,
			payload: {
				key: string,
			}
		) => StoreType
	}


export type MiddlewareFn<StoreType> = (
	accumulation: StoreType,
	state: StoreType,
	action: {
		type: string,
		payload?: any
	}
) => StoreType;

export type PayloadTypes<OuterDataShape, DataShape> =
	OuterDataShape |
	Error |
	((state: SimpleStore<OuterDataShape>) => void) |
	Partial<OuterDataShape> |
	DataShape |
	{
		key: string,
	}

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