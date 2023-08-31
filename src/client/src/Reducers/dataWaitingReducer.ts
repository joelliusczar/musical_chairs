import {
	MiddlewareFn,
	ReducerPaths,
	ActionPayload,
} from "./types/reducerTypes";
import { useWaitingReducer } from "./waitingReducer";
import { RequiredDataStore } from "../Reducers/reducerStores";

export const useDataWaitingReducer = <T, U=T>(
	initialState: RequiredDataStore<T>,
	setup?: {
		reducerMods?: Partial<ReducerPaths<T, RequiredDataStore<T>, U>>,
		middleware?: MiddlewareFn<ActionPayload<T, U>, RequiredDataStore<T>>[]
	}
) => {
	const { reducerMods, middleware } = (setup || {});
	return useWaitingReducer(initialState, {reducerMods, middleware});
};