import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { defaultWebClient as webClient } from "../../api";
import { CallType, CallStatus, UserRoleDef } from "../../constants";

export const login = createAsyncThunk(
	"accounts/login",
	async ({username, password}) => {
		const formData = new window.FormData();
		formData.append("username", username);
		formData.append("password", password);
		const response = await webClient.post("accounts/open", formData);
		return response.data;
	}
);

export const createAccount = async ({ values }) => {
	const response = await webClient.post("accounts/new", values);
	return response.data;
};

export const checkValues = async ({ values }) => {
	const response = await webClient.get("accounts/check", {
		params: values,
	});
	return response.data;
};


const initialState = {
	status: {
		[CallType.post]: "",
		[CallType.fetch]: "",
	},
	values: {
		[CallType.post]:{
			userId: "",
			username: "",
			roles: [],
			access_token: "",
			lifetime: 0,
		},
		[CallType.fetch]: {
			roles: [],
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

export const isAdminSelector = appState =>
	appState.accounts.values[CallType.post].roles
		.some(r => r.startsWith(UserRoleDef.ADMIN));

export const currentUserSelector = appState =>
	appState.accounts.values[CallType.post];

export const logout = slice.actions.logout;

export default slice.reducer;