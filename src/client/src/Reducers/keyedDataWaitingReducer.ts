import { useReducer } from "react";
import { 
	WaitingTypes,
	KeyedStoreShape,
} from "../Types/reducerTypes";
import { CallStatus } from "../constants";
import { RequiredDataStore } from "./reducerStores";
import { Dictionary, KeyValue } from "../Types/generic_types";
import clone from "just-clone";

export type KeyedDataActionPayload<T> = {
	type: WaitingTypes.started,
	payload: { keys: KeyValue[] }
} | {	
	type: WaitingTypes.done,
	payload: Dictionary<T>
} | {
	type: WaitingTypes.failed,
	payload: Dictionary<string>,
} | {
		type: WaitingTypes.restart,
		payload: { keys?: KeyValue[] }
} | {
		type: WaitingTypes.run,
		payload: ((state: KeyedStoreShape<RequiredDataStore<T | null>>) => void)
}  


export const keyedDataDispatches = {
	started: (keys: KeyValue[] ) =>
		({
			type: WaitingTypes.started,
			payload: { keys: keys },
		}) as { type: WaitingTypes.started, payload: { keys: KeyValue[] } },
	done: <T>(payload: Dictionary<T>) =>
		({
			type: WaitingTypes.done,
			payload: payload,
		}) as { 
			type: WaitingTypes.done,
			payload: Dictionary<T> 
		},
	failed: (data: Dictionary<string>) =>
		({
			type: WaitingTypes.failed,
			payload: data,
		}) as { 
			type: WaitingTypes.failed, 
			payload: Dictionary<string>,
		},
	restart: (keys?: KeyValue[]) => ({ 
		type: WaitingTypes.restart,
		payload: { 
			keys,
		} as typeof keys extends undefined ? undefined : {keys: KeyValue[]},
	}) as { 
		type: WaitingTypes.restart,
		payload: typeof keys extends undefined ? undefined : { keys: KeyValue[] },
	},
	run: <T>(
		fn:(
			data: KeyedStoreShape<RequiredDataStore<T | null>>
		) => void) => ({ 
			type: WaitingTypes.run, 
			payload: fn,
		}) as { 
		type: WaitingTypes.run, 
		payload:((data: KeyedStoreShape<RequiredDataStore<T | null>>) => void)},

};

export const keyedDataReducer = <T>(
	state: Dictionary<RequiredDataStore<T | null>>,
	action: KeyedDataActionPayload<T>
): Dictionary<RequiredDataStore<T | null>> => {
	switch(action.type) {
	case WaitingTypes.started:
	{	
		const { keys } = action.payload;
		const stateCopy = {...state};
		keys.forEach(k => {
			stateCopy[k] = {
				...stateCopy[k],
				callStatus: CallStatus.loading,
			};
		});
		return stateCopy;
	}
	case WaitingTypes.done:
	{
		const addedData: Dictionary<RequiredDataStore<T>> = {};
		Object.keys(action.payload).forEach((key) => {
			const payload = {
				data: action.payload[key],
				callStatus: CallStatus.done,
				error: null,
			};
			addedData[key] = payload;
		});

		return {
			...state,
			...addedData,
		};
	}
	case WaitingTypes.failed:
	{
		const addedData: Dictionary<RequiredDataStore<T | null>> = {};
		Object.keys(action.payload).forEach((key) => {
			const payload = {
				data: null,
				callStatus: CallStatus.failed,
				error: action.payload[key],
			};
			addedData[key] = payload;
		});
		
		return {
			...state,
			...addedData,
		};
	}
	case WaitingTypes.restart:
	{
		const { keys } = action.payload;
		if (!keys) {
			return {};
		}
		const stateCopy = {...state};
		keys.forEach(k => {
			stateCopy[k] = {
				...stateCopy[k],
				data: null,
				error: null,
				callStatus: null,
			};
		});
		return stateCopy;
	}
	case WaitingTypes.run:
		const deepCopy = clone(state);
		action.payload(deepCopy);
		return state;
	default:
		return state;
	}
};

export const useKeyedDataWaitingReducer = <T>() => {

	const initialState = {};
	return useReducer(keyedDataReducer<T>, initialState);
};