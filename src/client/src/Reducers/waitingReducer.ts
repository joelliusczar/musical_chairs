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

export const constructWaitingReducerMap = <T>() => {
	return {
		[WaitingTypes.started]: (state: SimpleStoreShape<T>) =>
			({
				...state,
				callStatus: CallStatus.loading,
			}),
		[WaitingTypes.restart]: (state: SimpleStoreShape<T>) =>
			({
				...state,
				callStatus: null,
			}),
		[WaitingTypes.done]: (state: SimpleStoreShape<T>, payload: T) =>
			({
				...state,
				callStatus: CallStatus.done,
				data: payload,
			}),
		[WaitingTypes.failed]: (state: SimpleStoreShape<T>, payload: string) =>
			({
				...state,
				callStatus: CallStatus.failed,
				error: payload,
			}),
		[WaitingTypes.reset]: (_: unknown, payload: T) =>
			({
				callStatus: null,
				data: payload,
				error: null,
			}),
		[WaitingTypes.read]: (
			state: SimpleStoreShape<T>,
			payload: (state: SimpleStoreShape<T>) => void
		) =>
		{
			const deepCopy = clone(state);
			payload(deepCopy);
			return state;
		},
		[WaitingTypes.assign]: (
			state: SimpleStoreShape<T>,
			payload: Partial<SimpleStoreShape<T>>
		) =>
			({
				...state,
				data: {
					...state.data,
					...payload,
				},
			}),
	};
};




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

	const waitingReducerMap = constructWaitingReducerMap<T>();
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

