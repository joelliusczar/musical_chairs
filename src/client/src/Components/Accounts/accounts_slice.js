import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { defaultWebClient as webClient } from "../../api";
import { ApiRoutes, CallType, CallStatus } from "../../constants";

export const login = createAsyncThunk(
	"accounts/login",
	async ({username, password}) => {
		const formData = new window.FormData();
		formData.append("username", username);
		formData.append("password", password);
		const response = await webClient.post(ApiRoutes.login, formData);
		return response.data;
	}
);

const initialState = {
	status: {
		[CallType.post]: "",
	},
	values: {
		[CallType.post]:{
			username: "",
			roles: [],
			access_token: "",
			lifetime: 0,
		},
	},
	error: {},
};

const slice = createSlice({
	name: "accounts",
	initialState,
	reducers: {
		logout: (state) => {
			state.values[CallType.post] = {...initialState.values[CallType.post]};
		},
	},
	extraReducers: {
		[login.pending]: (state) => {
			state.status[CallType.post] = CallStatus.loading;
		},
		[login.fulfilled]: (state, action) => {
			state.status[CallType.post] = CallStatus.done;
			state.values[CallType.post] = action.payload;
		},
		[login.rejected]: (state, action) => {
			state.status[CallType.post] = CallStatus.done;
			state.values[CallType.post] = action.payload;
		},
	},
});

export const logout = slice.actions.logout;

export default slice.reducer;