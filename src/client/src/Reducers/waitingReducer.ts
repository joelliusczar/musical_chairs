import { useReducer } from "react";
import clone from "just-clone";
import { CallStatus } from "../constants";
import {
	Dispatches,
	WaitingTypes,
	SimpleStoreShape,
	KeyAndData,
	MiddlewareFn,
	ReducerPaths,
	ActionPayload,
	AnonReducer,
} from "./types/reducerTypes";
import { RequiredDataStore } from "./reducerStores";



export const dispatches: Dispatches = {
	started: <T,>(payload?: T) =>
		({
			type: WaitingTypes.started,
			payload: payload,
		}) as { type: WaitingTypes.started, payload: T },
	restart: () => ({ type: WaitingTypes.restart }),
	done: <T,>(payload?: T) =>
		({
			type: WaitingTypes.done,
			payload: payload,
		}) as { type: WaitingTypes.done, payload: T },
	failed: <T extends KeyAndData<string> | string>(payload: T) =>
		({
			type: WaitingTypes.failed,
			payload: payload as T extends string ? string : KeyAndData<string>,
		}),
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


export class WaitingReducerMap<T>
{
	started(state: SimpleStoreShape<T>): SimpleStoreShape<T> {
		return {
			...state,
			callStatus: CallStatus.loading,
		};
	}

	restart(state: SimpleStoreShape<T>): SimpleStoreShape<T> {
		return {
			...state,
			callStatus: null,
		};
	}

	done(
		state:SimpleStoreShape<T>,
		payload: T
	): SimpleStoreShape<T>
	{
		return {
			...state,
			callStatus: CallStatus.done,
			data: payload,
		};
	}

	failed(
		state: SimpleStoreShape<T>,
		payload: string
	): SimpleStoreShape<T>
	{
		return {
			...state,
			callStatus: CallStatus.failed,
			error: payload,
		};
	}

	reset(_: unknown, payload: T): SimpleStoreShape<T> {
		return {
			callStatus: null,
			data: payload,
			error: null,
		};
	}

	read(
		state: SimpleStoreShape<T>,
		payload: (state: SimpleStoreShape<T>) => void
	): SimpleStoreShape<T>
	{
		const deepCopy = clone(state);
		payload(deepCopy);
		return state;
	}

	assign(
		state: SimpleStoreShape<T>,
		payload: Partial<SimpleStoreShape<T>>
	): SimpleStoreShape<T>
	{
		return {
			...state,
			data: {
				...state.data,
				...payload,
			},
		};
	}
}



export const globalStoreLogger =
(name: string) =>
	<StoreType>(
		result: StoreType,
		state: StoreType,
		action: { type: unknown, payload?: unknown }
	) => {

		console.info(`${name} : ${action.type}`);
		console.info("Previous: ", state);
		console.info("Payload: ", action?.payload);
		console.info("Next: ", result);
		return result;
	};



export const waitingReducer = <T, StoreType=RequiredDataStore<T>, U=T>(
	{ reducerMods, middleware }: {
		reducerMods?: Partial<ReducerPaths<T, StoreType, U>>,
		middleware?: MiddlewareFn<ActionPayload<T, U>, StoreType>[]
	}
):
(
	(
		state: StoreType,
		action: ActionPayload<T, U>
	) => StoreType
) =>
{

	const waitingReducerMap = new WaitingReducerMap<T>();
	const reducerMap = {
		...waitingReducerMap,
		...reducerMods,
	} as ReducerPaths<T, StoreType, U>;

	if (!Array.isArray(middleware)) {
		middleware = [];
	}

	return (
		state: StoreType,
		action: ActionPayload<T, U>
	) => {
		if (action.type in reducerMap) {
			const reducer = reducerMap[action.type] as AnonReducer<StoreType>;
			if (reducer) {
				const initialValue = reducer(state, action.payload);
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



export const useWaitingReducer = <T, StoreType = RequiredDataStore<T>, U=T>(
	initialState: StoreType,
	setup?: {
		reducerMods?: Partial<ReducerPaths<T, StoreType, U>>,
		middleware?: MiddlewareFn<ActionPayload<T, U>, StoreType>[]
	}
) => {
	const { reducerMods, middleware } = (setup || {});

	const reducer = waitingReducer<T,StoreType, U>({reducerMods, middleware});

	return useReducer(reducer, initialState);
};

