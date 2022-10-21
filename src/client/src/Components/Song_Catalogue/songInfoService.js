import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import webClient from "../../API_Calls/api";
import { CallStatus, ApiRoutes, CallType } from "../../constants";

export const fetchSongCatalogue = createAsyncThunk(
	"song_catalogue/fetch",
	async ({ station, params }) => {

		const response = await webClient
			.get(`${ApiRoutes.songCatalogue(station)}`, {
				params: params,
			});
		return response.data;
	}
);

const initialState = {
	status: {
		[CallType.fetch]: "",
	},
	values: {
		[CallType.fetch]:{
			totalRows: 0,
			items: [],
		},
	},
	error: {},
};

const slice = createSlice({
	name: "song_catalogue",
	initialState,
	extraReducers: {
		[fetchSongCatalogue.pending]: (state) => {
			state.status[CallType.fetch] = CallStatus.loading;
		},
		[fetchSongCatalogue.fulfilled]: (state, action) => {
			state.status[CallType.fetch] = CallStatus.done;
			state.values[CallType.fetch] = action.payload;
		},
		[fetchSongCatalogue.rejected]: (state, action) => {
			state.status[CallType.fetch] = CallStatus.failed;
			state.error[CallType.fetch] = action.error;
		},
	},
});

export default slice.reducer;
