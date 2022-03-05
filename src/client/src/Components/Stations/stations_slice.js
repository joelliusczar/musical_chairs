import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../api";
import { CallStatus, ApiRoutes, CallType } from "../../constants";

export const fetchStations = createAsyncThunk("stations/fetch", async () => {
	const response = await webClient.get(ApiRoutes.stations());
	return response.data;
});

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
};

const slice = createSlice({
	name: "stations",
	initialState,
	extraReducers: {
		[fetchStations.pending]: (state) => {
			state.status[CallType.fetch] = CallStatus.loading;
		},
		[fetchStations.fulfilled]: (state, action) => {
			state.status[CallType.fetch] = CallStatus.done;
			state.values[CallType.fetch] = action.payload;
		},
		[fetchStations.rejected]: (state, action) => {
			state.status[CallType.fetch] = CallStatus.failed;
			state.error[CallType.fetch] = action.error;
		},
	},
});

export default slice.reducer;
