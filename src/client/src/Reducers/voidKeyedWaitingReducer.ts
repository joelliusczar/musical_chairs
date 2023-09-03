import { useReducer } from "react";
import { CallStatus } from "../constants";
import { KeyType } from "../Types/generic_types";
import {
	KeyAndData,
	KeyedStoreShape,
	VoidStoreShape,
	MiddlewareFn,
	AnonReducer,
	WaitingTypes,
} from "./types/reducerTypes";
import {
	VoidKeyedActionPayload,
	VoidKeyedUnionSelect,
} from "./types/voidKeyedReducerTypes";

export const constructVoidKeyedWaitingReducerPaths = () => {
	return {
		[WaitingTypes.started]: (
			state: KeyedStoreShape<VoidStoreShape>,
			payload: { key: KeyType }
		) => {
			const { key } = payload;
			return {
				...state,
				[key]: {
					...state[key],
					callStatus: CallStatus.loading,
				},
			};
		},
		[WaitingTypes.done]: (
			state: KeyedStoreShape<VoidStoreShape>,
			payload: { key: KeyType }
		) => {
			const { key } = payload;
			return {
				...state,
				[key]: {
					...state[key],
					callStatus: CallStatus.done,
				},
			};
		},
		[WaitingTypes.failed]: (
			state: KeyedStoreShape<VoidStoreShape>,
			payload: KeyAndData<string>
		) => {
			const { key, data } = payload;
			return {
				...state,
				[key]: {
					...state[key],
					callStatus: CallStatus.failed,
					error: data,
				},
			};
		},
		[WaitingTypes.reset]: (
			state: KeyedStoreShape<VoidStoreShape>,
			payload: { key: KeyType }
		) => {
			const { key } = payload;
			return {
				...state,
				[key]: {
					callStatus: null,
					error: null,
				},
			};
		},
	};
};


export const useVoidKeyedWaitingReducer = (
	initialState: KeyedStoreShape<VoidStoreShape>,
	reducerMods?: Partial<VoidKeyedUnionSelect>,
	middleware?: MiddlewareFn<
		VoidKeyedActionPayload,
		KeyedStoreShape<VoidStoreShape>
	>[]
) => {
	const waitingReducerMap = constructVoidKeyedWaitingReducerPaths();
	const reducerMap = {
		...waitingReducerMap,
		...reducerMods,
	};

	if (!Array.isArray(middleware)) {
		middleware = [];
	}

	const wrappedFn = (
		state: KeyedStoreShape<VoidStoreShape>,
		action: VoidKeyedActionPayload
	) => {
		if (action.type in reducerMap) {
			const reducer =
				reducerMap[action.type] as AnonReducer<KeyedStoreShape<VoidStoreShape>>;
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

	return useReducer(wrappedFn, initialState);
};