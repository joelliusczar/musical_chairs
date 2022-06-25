import { CallStatus } from "../../constants";

export const initialState = {
	callStatus: null,
	data: {},
	error: null,
};

export const listDataInitialState = {
	...initialState,
	data: {
		items: [],
	},
};

export const pageableDataInitialState = {
	...listDataInitialState,
	data: {
		...listDataInitialState.data,
		totalRows: 0,
	},
};


export const waitingTypes = {
	started: "started",
	done: "done",
	failed: "failed",
	reset: "reset",
	add: "add", //implemented as needed
	remove: "remove", //implemented as needed
};

export const dispatches = {
	started: () => ({ type: waitingTypes.started }),
	done: (payload) => ({ type: waitingTypes.done, payload: payload }),
	failed: (payload) => ({ type: waitingTypes.failed, payload: payload }),
	reset: (payload) => ({ type: waitingTypes.reset, payload: payload }),
	add: (payload) => ({ type: waitingTypes.add, payload: payload }),
	remove: (payload) => ({ type: waitingTypes.remove, payload: payload }),
};

export const waitingReducerMap = {
	[waitingTypes.started]: (state) =>
		({
			...state,
			callStatus: CallStatus.loading,
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
	[waitingTypes.reset]: (payload) =>
		({
			callStatus: null,
			data: payload,
			error: null,
		}),
};

export const waitingReducer = (reducerMods=null) => {

	const reducerMap = {
		...waitingReducerMap,
		...reducerMods,
	};

	return (state, action) => {
		if(action.type in reducerMap) {
			return reducerMap[action.type](state, action.payload);
		}
		else {
			return state;
		}
	};
};