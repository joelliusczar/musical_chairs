import clone from "just-clone";
import { CallStatus } from "../../constants";

export const voidState = {
	callStatus: null,
	error: null,
};

export const initialState = {
	...voidState,
	data: {},
};

export const listDataInitialState = {
	...initialState,
	data: {
		items: [],
	},
};

export const pageableDataInitialState = {
	...initialState,
	data: {
		items: [],
		totalRows: 0,
	},
};


export const waitingTypes = {
	started: "started",
	restart: "restart",
	done: "done",
	failed: "failed",
	reset: "reset",
	read: "read",
	add: "add", //implemented as needed
	update: "update", //implemented as needed
	remove: "remove", //implemented as needed
	assign: "assign", //implemented as needed
};

export const dispatches = {
	started: (payload) => ({ type: waitingTypes.started, payload: payload }),
	restart: () => ({ type: waitingTypes.restart }),
	done: (payload) => ({ type: waitingTypes.done, payload: payload }),
	failed: (payload) => ({ type: waitingTypes.failed, payload: payload }),
	reset: (payload) => ({ type: waitingTypes.reset, payload: payload }),
	add: (payload) => ({ type: waitingTypes.add, payload: payload }),
	update: (key, dataOrUpdater) =>
		({ type: waitingTypes.update, payload: { key, dataOrUpdater } }),
	remove: (payload) => ({ type: waitingTypes.remove, payload: payload }),
	assign: (payload) => ({ type: waitingTypes.assign, payload: payload}),
	read: (fn) => ({ type: waitingTypes.read, payload: fn}),
};

export const waitingReducerMap = {
	[waitingTypes.started]: (state) =>
		({
			...state,
			callStatus: CallStatus.loading,
		}),
	[waitingTypes.restart]: (state) =>
		({
			...state,
			callStatus: null,
		}),
	[waitingTypes.done]: (state, payload) =>
		({
			...state,
			callStatus: CallStatus.done,
			data: payload,
		}),
	[waitingTypes.failed]: (state, payload) =>
		({
			...state,
			callStatus: CallStatus.failed,
			error: payload,
		}),
	[waitingTypes.reset]: (_, payload) =>
		({
			callStatus: null,
			data: payload,
			error: null,
		}),
	[waitingTypes.read]: (state, payload) =>
	{
		const deepCopy = clone(state);
		payload(deepCopy);
		return state;
	},
	[waitingTypes.assign]: (state, payload) =>
		({
			...state,
			data: {
				...state.data,
				...payload,
			},
		}),
};

export const globalStoreLogger = (name) =>
	(result, state, action, reducerMap) => {
		if (!(action.type in reducerMap)) {
			console.info("Action type is not mapped. ");
			return result;
		}
		console.info(`${name} : ${action.type}`);
		console.info("Previous: ", state);
		console.info("Payload: ", action.payload);
		console.info("Next: ", result);
		return result;
	};

export const waitingReducer = (reducerMods=null, middleware=null) => {

	const reducerMap = {
		...waitingReducerMap,
		...reducerMods,
	};

	if (!middleware || !Array.isArray(middleware)) {
		middleware = [];
	}

	return (state, action) => {
		if (action.type in reducerMap) {
			return middleware.reduce(
				(accumulation, mFn) => mFn(accumulation, state, action, reducerMap),
				reducerMap[action.type](state, action.payload)
			);
		}
		else {
			return middleware.reduce(
				(accumulation, mFn) => mFn(accumulation, state, action, reducerMap),
				state
			);
		}
	};
};

export const keyedWaitingReducerMap = {
	[waitingTypes.started]: (state, payload) => {
		const { key } = payload;
		return {
			...state,
			[key]: {
				...state[key],
				callStatus: CallStatus.loading,
			},
		};
	},
	[waitingTypes.done]: (state, payload) => {
		const { key, data } = payload;
		return {
			...state,
			[key]: {
				...state[key],
				callStatus: CallStatus.done,
				data: data,
			},
		};
	},
	[waitingTypes.failed]: (state, payload) => {
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
	[waitingTypes.reset]: (state, payload) => {
		const { key, data } = payload;
		return {
			...state,
			[key]: {
				callStatus: null,
				error: null,
				data: data,
			},
		};
	},
};