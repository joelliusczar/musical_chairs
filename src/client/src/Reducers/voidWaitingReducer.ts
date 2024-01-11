import { useReducer } from "react";
import { 
	WaitingTypes,
} from "../Types/reducerTypes";
import { CallStatus } from "../constants";
import { VoidStore } from "./reducerStores";
import clone from "just-clone";
import { KeyValue } from "../Types/generic_types";

export type VoidActionPayload = {
	type: WaitingTypes.started,
	payload?: KeyValue,
} | {	
	type: WaitingTypes.done
} | {
	type: WaitingTypes.failed,
	payload: string
} | {
	type: WaitingTypes.restart
} | {
	type: WaitingTypes.run,
	payload: ((state: VoidStore) => void)
}

export const voidDispatches = {
	started: (key?: KeyValue) =>
		({
			type: WaitingTypes.started,
			payload: key,
		}) as { type: WaitingTypes.started, payload?: KeyValue },
	done: () =>
		({
			type: WaitingTypes.done,
		}) as { type: WaitingTypes.done },
	failed: (payload: string) =>
		({
			type: WaitingTypes.failed,
			payload: payload,
		}) as { type: WaitingTypes.failed, payload: string },
	restart: () => ({ 
		type: WaitingTypes.restart, 
	}) as { type: WaitingTypes.restart },
	run: <T>(fn:(data: T) => void) => ({ 
		type: WaitingTypes.run,
		payload: fn,
	}) as { type: WaitingTypes.run, payload:((data: T) => void)},
};

export const voidReducer = (
	state: VoidStore,
	action: VoidActionPayload
): VoidStore => {
	switch(action.type) {
	case WaitingTypes.started:
		return {
			...state,
			key: action.payload,
			callStatus: CallStatus.loading,
		};
	case WaitingTypes.done:
		return {
			...state,
			callStatus: CallStatus.done,
		};
	case WaitingTypes.failed:
		return {
			...state,
			callStatus: CallStatus.failed,
			error: action.payload,
		};
	case WaitingTypes.restart:
		return {
			...state,
			key: "",
			callStatus: null,
			error: null,
		};
	case WaitingTypes.run:
		const deepCopy = clone(state);
		action.payload(deepCopy);
		return state;
	default:
		return state;
	}
};

export const useVoidWaitingReducer = (initialState?: VoidStore) => {
	const state = initialState || new VoidStore();
	return useReducer(voidReducer, state);
};