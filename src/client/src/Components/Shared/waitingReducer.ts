import { useReducer } from "react";
import clone from "just-clone";
import { CallStatus } from "../../constants";
import { NamedIdItem } from "../../Types/generic_types";
import {
	Dispatches,
	WaitingTypes,
	SimpleStore,
	KeyAndData,
	MiddlewareFn,
	ReducerMods,
	KeyedStore,
	InitialState,
	ActionPayloadType,
	RequiredDataState,
	PageableListDataShape,
	KeyAndDataOrUpdater,
	ListStore,
	ListDataShape,
	VoidState
} from "../../Types/reducer_types";
import { StationTableData } from "../../Types/station_types";
import {
	InitialQueueState,
	CurrentPlayingInfo
} from "../../Types/song_info_types";
import { nameSortFn } from "../../Helpers/array_helpers";



export const dispatches: Dispatches = {
	started: (payload) =>
		({ type: WaitingTypes.started, payload: payload }),
	restart: () => ({ type: WaitingTypes.restart }),
	done: (payload) => ({ type: WaitingTypes.done, payload: payload }),
	failed: (payload) => ({ type: WaitingTypes.failed, payload: payload }),
	reset: (payload) => ({ type: WaitingTypes.reset, payload: payload }),
	add: (payload) =>
		({ type: WaitingTypes.add, payload: payload }),
	update: (key, dataOrUpdater) =>
		({ type: WaitingTypes.updateItem, payload: { key, dataOrUpdater } }),
	remove: (key) =>
		({ type: WaitingTypes.remove, payload: { key } }),
	assign: (payload) => ({ type: WaitingTypes.assign, payload: payload}),
	read: (fn) => ({ type: WaitingTypes.read, payload: fn}),
};


export class WaitingReducerMap<DataShape>
{
	started(state: SimpleStore<DataShape>): SimpleStore<DataShape> {
			return {
				...state,
			callStatus: CallStatus.loading,
		}
	}

	restart(state: SimpleStore<DataShape>): SimpleStore<DataShape> {
		return {
			...state,
			callStatus: null,
		};
	}

	done(
		state:SimpleStore<DataShape>,
		payload: DataShape
	): SimpleStore<DataShape>
	{
		return {
			...state,
			callStatus: CallStatus.done,
			data: payload,
		};
	}

	failed(
		state: SimpleStore<DataShape>,
		payload: string
	): SimpleStore<DataShape>
	{
		return {
			...state,
			callStatus: CallStatus.failed,
			error: payload,
		};
	}

	reset(_: unknown, payload: DataShape): SimpleStore<DataShape> {
		return {
			callStatus: null,
			data: payload,
			error: null,
		};
	}

	read(
		state: SimpleStore<DataShape>,
		payload: (state: SimpleStore<DataShape>) => void
	): SimpleStore<DataShape>
	{
		const deepCopy = clone(state);
		payload(deepCopy);
		return state;
	}

	assign(
		state: SimpleStore<DataShape>,
		payload: Partial<SimpleStore<DataShape>>
	): SimpleStore<DataShape>
	{
		return {
			...state,
			data: {
				...state.data,
				...payload,
			},
		}
	}
};

class SortedListReducerPaths<DataShape extends NamedIdItem> {
	done(state: ListStore<DataShape>, payload?: ListDataShape<DataShape>) {
		const items = payload && payload.items ? payload.items
			.sort(nameSortFn)
			: [];
		return {
			...state,
			data: {
				items: items,
			},
			callStatus: CallStatus.done,
		};
	}
	add(state: ListStore<DataShape>, payload: DataShape) {
		const items = [...state.data.items, payload]
			.sort(nameSortFn);
		return {
			...state,
			data: {
				items: items,
			},
		};
	}
	update(
		state: ListStore<DataShape>,
		payload: KeyAndDataOrUpdater<DataShape>
	) {
		const { key, dataOrUpdater } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === (+key * 1));
		if (idx > -1) {
			if (typeof dataOrUpdater === "function") {
				items.splice(idx, 1, dataOrUpdater(items[idx]));
			}
			else {
				items.splice(idx, 1, dataOrUpdater);
			}
			const sortedItems = items.sort(nameSortFn);
			return {
				...state,
				data: {
					items: sortedItems,
				},
			};
		}
		else {
			console.error("Item was not found in local store.");
		}
	}
};


export const globalStoreLogger: <
	T,
	StoreType = InitialState<T>,
	U=T
>(name: string) => MiddlewareFn<T,StoreType, U> =
(name: string) =>
	(result, state, action) => {

		console.info(`${name} : ${action.type}`);
		console.info("Previous: ", state);
		console.info("Payload: ", action.payload);
		console.info("Next: ", result);
		return result;
	};


export const waitingReducer = <T, StoreType=InitialState<T>, U=T>(
	reducerMods?: Partial<ReducerMods<T, StoreType, U>>,
	middleware?: MiddlewareFn<T, StoreType, U>[]
):
(
	(
		state: StoreType,
		action: ActionPayloadType<T, U>
	) => StoreType
) =>
{

	const waitingReducerMap = new WaitingReducerMap<T>();
	const reducerMap = {
		...waitingReducerMap,
		...reducerMods,
	} as ReducerMods<T, StoreType, U>;

	if (!Array.isArray(middleware)) {
		middleware = [];
	}

	return (
		state: StoreType,
		action: ActionPayloadType<T, U>
	) => {
		if (action.type in reducerMap) {
			const reducer = reducerMap[action.type];
			if (reducer) {
				const initialValue = reducer(state, action.payload as any);
				return middleware!.reduce(
					(accumulation, mFn) => mFn(accumulation, state, action),
					initialValue
				);
			}
		}
		return middleware!.reduce(
			(accumulation, mFn) => mFn(accumulation, state, action),
			state
		);
	};
};

export class KeyedWaitingReducerMap<DataShape> {
	started(
		state: KeyedStore<DataShape>,
		payload: { key: string }
	): KeyedStore<DataShape>
	{
		const { key } = payload;
		return {
			...state,
			[key]: {
				...state[key],
				callStatus: CallStatus.loading,
			},
		};
	}

	done(
		state: KeyedStore<DataShape>,
		payload: KeyAndData<DataShape>
	): KeyedStore<DataShape>
	{
		const { key, data } = payload;
		return {
			...state,
			[key]: {
				...state[key],
				callStatus: CallStatus.done,
				data: data,
			},
		};
	}

	failed(
		state: KeyedStore<DataShape>,
		payload: { key: string, data: string}
	): KeyedStore<DataShape>
	{
		const { key, data } = payload;
		return {
			...state,
			[key]: {
				...state[key],
				callStatus: CallStatus.failed,
				error: data,
			},
		};
	}

	reset(
		state: KeyedStore<DataShape>,
		payload: KeyAndData<DataShape>
	): KeyedStore<DataShape>{
		const { key, data } = payload;
		return {
			...state,
			[key]: {
				callStatus: null,
				error: null,
				data: data,
			},
		};
	}
};


export const useWaitingReducer = <T, StoreType = InitialState<T>, U=T>(
	initialState: StoreType,
	reducerMods?: Partial<ReducerMods<T, StoreType, U>>,
	middleware?: MiddlewareFn<T, StoreType, U>[]
) => {

	const reducer = waitingReducer<T,StoreType, U>(reducerMods, middleware);

	return useReducer(reducer, initialState);
};

export const useVoidWaitingReducer = (
	reducerMods?: Partial<ReducerMods<void, VoidState>>,
	middleware?: MiddlewareFn<void, VoidState>[]
) => {

	const initialState = new VoidState();
	return useWaitingReducer(initialState, reducerMods, middleware);
};


export const useDataWaitingReducer = <T, U=T>(
	initialState: RequiredDataState<T>,
	reducerMods?: Partial<ReducerMods<T, RequiredDataState<T>, U>>,
	middleware?: MiddlewareFn<T, RequiredDataState<T>, U>[]
) => {

	return useWaitingReducer(initialState, reducerMods, middleware);
};

export const usePageableWaitingReducer = <T, U=T>(
	initialState: RequiredDataState<PageableListDataShape<T>>,
	reducerMods?: Partial<
		ReducerMods<T, RequiredDataState<PageableListDataShape<T>>, T>
	>,
	middleware?: MiddlewareFn<
		T, RequiredDataState<PageableListDataShape<T>>, T
	>[]
) => {

	return useWaitingReducer(initialState, reducerMods, middleware);
};

export const useStationSongsWaitingReducer = <T>(
	initialState: RequiredDataState<StationTableData<T>>,
	reducerMods?: Partial<
		ReducerMods<T, RequiredDataState<StationTableData<T>>, T>
	>,
	middleware?: MiddlewareFn<
		T, RequiredDataState<StationTableData<T>>, T
	>[]
) => {

	return useWaitingReducer(initialState, reducerMods, middleware);
};

export const useSongQueueTableWaitingReducer = (
	reducerMods?: Partial<
		ReducerMods<CurrentPlayingInfo, InitialQueueState>
	>,
	middleware?: MiddlewareFn<CurrentPlayingInfo, InitialQueueState>[]
) => {
	const initialState = new InitialQueueState();
	return useWaitingReducer(initialState, reducerMods, middleware);
};

export const useListDataWaitingReducer = <T>(
	initialState: RequiredDataState<ListDataShape<T>>,
	reducerMods?: Partial<
		ReducerMods<T, RequiredDataState<ListDataShape<T>>, T>
	>,
	middleware?: MiddlewareFn<
		T, RequiredDataState<ListDataShape<T>>, T
	>[]
) => {

	return useWaitingReducer(initialState, reducerMods, middleware);
};

export const useKeyedWaitingReducer = <T>(
	initialState: {},
	reducerMods?: Partial<
		ReducerMods<T, KeyedStore<T>, T>
	>,
	middleware?: MiddlewareFn<
		T, KeyedStore<T>, T
	>[]
) => {

	const reducerMap = {
		...(new KeyedWaitingReducerMap<T>()),
		...reducerMods
	};

	return useWaitingReducer(initialState, reducerMap, middleware);
};