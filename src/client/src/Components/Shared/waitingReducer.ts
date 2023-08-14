import clone from "just-clone";
import { CallStatus } from "../../constants";
import {
	Dispatches,
	WaitingTypes,
	SimpleStore,
	KeyAndData,
	MiddlewareFn,
	ReducerMods,
	KeyedStore,
	InitialState,
} from "../../Types/reducer_types";
import { Error } from "../../Types/generic_types";



// export const listDataInitialState = {
// 	...InitialState,
// 	data: {
// 		items: [],
// 	},
// };

// export const pageableDataInitialState = {
// 	...InitialState,
// 	data: {
// 		items: [],
// 		totalRows: 0,
// 	},
// };



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

export const globalStoreLogger: <T>(name: string) => MiddlewareFn<T> =
(name: string) =>
	(result, state, action) => {

		console.info(`${name} : ${action.type}`);
		console.info("Previous: ", state);
		console.info("Payload: ", action.payload);
		console.info("Next: ", result);
		return result;
	};


export const waitingReducer = <DataShape, StoreType = InitialState<DataShape>>(
	reducerMods: Partial<ReducerMods<DataShape, StoreType>> | null=null,
	middleware: MiddlewareFn<StoreType>[] | null=null
):
(
	(
		state: StoreType,
		action: { type: WaitingTypes, payload: any}
	) => StoreType
) =>
{

	const waitingReducerMap = new WaitingReducerMap<DataShape>();
	const reducerMap = {
		...waitingReducerMap,
		...reducerMods,
	} as ReducerMods<DataShape, StoreType>;

	if (!Array.isArray(middleware)) {
		middleware = [];
	}

	return (
		state: StoreType,
		action: {
			type: WaitingTypes,
			payload: any
		}
	) => {
		if (action.type in reducerMap) {
			const reducer = reducerMap[action.type];
			const initialValue = reducer!(state, action.payload);
			return middleware!.reduce(
				(accumulation, mFn) => mFn(accumulation, state, action),
				initialValue
			);
		}
		else {
			return middleware!.reduce(
				(accumulation, mFn) => mFn(accumulation, state, action),
				state
			);
		}
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