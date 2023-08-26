import {
	VoidStoreShape,
	ReducerPaths,
	MiddlewareFn,
	ActionPayload
} from "./types/reducerTypes";
import { useWaitingReducer } from "./waitingReducer";
import { VoidStore } from "./reducerStores";

export const useVoidWaitingReducer = (
	setup?: {
		reducerMods?: Partial<ReducerPaths<void, VoidStoreShape>>,
		middleware?: MiddlewareFn<ActionPayload<void>, VoidStoreShape>[]
	}
) => {

	const { reducerMods, middleware} = (setup || {});
	const initialState = new VoidStore();
	return useWaitingReducer(initialState, { reducerMods, middleware });
};