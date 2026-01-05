import { useReducer } from "react";
import clone from "just-clone";
import { 
	WaitingTypes,
} from "../Types/reducerTypes";
import { CallStatus } from "../constants";
import { RequiredDataStore } from "./reducerStores";





export type DataActionPayload<T> = {
	type: WaitingTypes.started;
} | {	
type: WaitingTypes.done,
payload: T
} | {
	type: WaitingTypes.stopped,
} |{
	type: WaitingTypes.failed,
	payload: string
} | {
	type: WaitingTypes.restart
} | {
	type: WaitingTypes.set,
	payload: T
} | {
	type: WaitingTypes.run,
	payload: ((state: RequiredDataStore<T>) => void)
} | {
	type: WaitingTypes.assign,
	payload: Partial<T>
} | {
	type: WaitingTypes.update,
	payload: ((state: RequiredDataStore<T>) => RequiredDataStore<T>)
};

export const dataDispatches = {
	started: () =>
		({
			type: WaitingTypes.started,
		}) as { type: WaitingTypes.started },
	done: <T>(payload: T) =>
		({
			type: WaitingTypes.done,
			payload: payload,
		}) as { type: WaitingTypes.done, payload: T },
	stopped: () => ({
		type: WaitingTypes.done,
	}),
	failed: (payload: string) =>
		({
			type: WaitingTypes.failed,
			payload: payload,
		}) as { type: WaitingTypes.failed, payload: string },
	restart: () => ({ 
		type: WaitingTypes.restart,
	}) as { type: WaitingTypes.restart},
	set: <T>(payload: T) => 
		({ 
			type: WaitingTypes.set,
			payload: payload,
		}) as { type: WaitingTypes.set, payload: T },
	assign: <T>(payload: T) => ({ 
		type: WaitingTypes.assign,
		payload: payload,
	}) as { type: WaitingTypes.assign, payload: T },
	run: <T>(fn:(data: T) => void) => ({ 
		type: WaitingTypes.run,
		payload: fn,
	}) as { type: WaitingTypes.run, payload: (data: T) => void },
	update: <T>(fn:(data: T) => T) => ({ 
		type: WaitingTypes.update, 
		payload: fn,
	}) as { type: WaitingTypes.update, payload: (data: T) => T },
};




export const useDataWaitingReducer = <T>(
	initialState: RequiredDataStore<T>) => {

	const dataReducer = (
		state: RequiredDataStore<T>,
		action: DataActionPayload<T>
	): RequiredDataStore<T> => {
		switch(action.type) {
		case WaitingTypes.started:
			return {
				...state,
				callStatus: CallStatus.loading,
				error: null,
			};
		case WaitingTypes.done:
			return {
				...state,
				callStatus: CallStatus.done,
				data: action.payload,
				error: null,
			};
		case WaitingTypes.stopped:
			return {
				...state,
				callStatus: CallStatus.done,
				error: null,
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
				callStatus: null,
				error: null,
			};
		case WaitingTypes.set:
			return {
				...state,
				data: action.payload,
				callStatus: null,
				error: null,
			};
		case WaitingTypes.run:
			const deepCopy = clone(state);
			action.payload(deepCopy);
			return state;
		case WaitingTypes.assign:
			return {
				...state,
				data: {
					...state.data,
					...action.payload,
				},
			};
		case WaitingTypes.update:
			const newState = action.payload({...state});
			return newState;
		default:
			return state;
		}
	};

	return useReducer(dataReducer, initialState);
};