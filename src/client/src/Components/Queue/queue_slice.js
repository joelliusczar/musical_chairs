import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../api";
import { CallStatus, ApiRoutes, CallType } from "../../constants";

export const fetchQueue = createAsyncThunk(
	"queue/fetch",
	async ({ station }) => {
		const response = await webClient.get(ApiRoutes.queue(station));
		return response.data;
	}
);

const initialState = {
	status: {
		[CallType.fetch]: "",
	},
	values: { 
		[CallType.fetch]:{
			items: [],
		},
	},
	error: {},
	refreshSignal: null,
};

const slice = createSlice({
	name: "queue",
	initialState,
	reducers: {
		sendRefreshSignal: (state) => {
			state.refreshSignal = {};
		},
	},
	extraReducers: {
		[fetchQueue.pending]: (state) => {
			state.status[CallType.fetch] = CallStatus.loading;
		},
		[fetchQueue.fulfilled]: (state, action) => {
			state.status[CallType.fetch] = CallStatus.done;
			state.values[CallType.fetch] = action.payload;
		},
		[fetchQueue.rejected]: (state, action) => {
			state.status[CallType.fetch] = CallStatus.failed;
			state.error[CallType.fetch] = action.error;
		},
	},
});

export default slice.reducer;
