import { useReducer } from "react";
import { 
	WaitingTypes,
	KeyedStoreShape,
} from "../Types/reducerTypes";
import { CallStatus } from "../constants";
import { VoidStore } from "./reducerStores";
import { KeyValue } from "../Types/generic_types";

export type KeyedVoidActionPayload = {
	type: WaitingTypes.started,
	payload: { keys: KeyValue[] }
} | {	
	type: WaitingTypes.done,
	payload: { keys: KeyValue[] }
} | {
	type: WaitingTypes.failed,
	payload: {key: KeyValue, msg: string }[],
} | {
		type: WaitingTypes.restart,
		payload: { keys: KeyValue[] }
} | {
		type: WaitingTypes.run,
		payload: ((state: KeyedStoreShape<VoidStore>) => void)
}  


export const keyedVoidDispatches = {
	started: (keys: KeyValue[] ) =>
		({
			type: WaitingTypes.started,
			payload: { keys: keys },
		}) as { type: WaitingTypes.started, payload: { keys: KeyValue[] } },
	done: (keys: KeyValue[]) =>
		({
			type: WaitingTypes.done,
			payload: { keys: keys },
		}) as { type: WaitingTypes.done, payload: { keys: KeyValue[] } },
	failed: (data: { key: KeyValue, msg: string }[]) =>
		({
			type: WaitingTypes.failed,
			payload: data,
		}) as { 
			type: WaitingTypes.failed, 
			payload: {key: KeyValue, msg: string}[],
		},
	restart: (keys: KeyValue[]) => ({ 
		type: WaitingTypes.restart,
		payload: { key: keys },
	}),
	run: <T>(fn:(data: T) => void) => ({ type: WaitingTypes.run, payload: fn}),

};

export const voidReducer = (
	state: KeyedStoreShape<VoidStore>,
	action: KeyedVoidActionPayload
): KeyedStoreShape<VoidStore> => {
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
		const { keys } = action.payload;
		const stateCopy = {...state};
		keys.forEach(k => {
			stateCopy[k] = {
				...stateCopy[k],
				callStatus: CallStatus.done,
			};
		});
		return stateCopy;
	}
	case WaitingTypes.failed:
	{
		const stateCopy = {...state};
		action.payload.forEach(item => {
			stateCopy[item.key] = {
				...stateCopy[item.key],
				callStatus: CallStatus.failed,
				error: item.msg,
			};
		});
		return stateCopy;
	}
	case WaitingTypes.restart:
	{
		const { keys } = action.payload;
		const stateCopy = {...state};
		keys.forEach(k => {
			stateCopy[k] = {
				...stateCopy[k],
				error: null,
				callStatus: null,
			};
		});
		return stateCopy;
	}
	default:
		return state;
	}
};

export const useKeyedVoidWaitingReducer = () => {

	const initialState = {};
	return useReducer(voidReducer, initialState);
};