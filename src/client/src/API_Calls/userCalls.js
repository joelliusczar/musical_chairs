import { createSlice } from "@reduxjs/toolkit";
import { defaultWebClient as webClient } from "./api";
import { CallStatus, UserRoleDef } from "../constants";

export const AccountsCallTypes = {
	login: "login",
};


export const login = async ({username, password}) => {
	const formData = new window.FormData();
	formData.append("username", username);
	formData.append("password", password);
	const response = await webClient.post("accounts/open", formData);
	webClient.defaults.headers.common["Authorization"] =
	`Bearer ${response.data.access_token}`;
	return response.data;
};

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

export const fetchUser = async ({ id }) => {
	const response = await webClient.get(`accounts/${id}`);
	return response.data;
};

export const fetchUserList = async ({ params }) => {
	const response = await webClient.get("accounts/list", {
		params: params,
	});
	return response.data;
};

export const updateUserRoles = async ({ id, roles }) => {
	const response = await webClient.put(`accounts/update-roles/${id}`,
		roles
	);
	return response.data;
};

const initialState = {
	status: {
		[AccountsCallTypes.login]: "",
		[AccountsCallTypes.fetch]: "",
	},
	values: {
		[AccountsCallTypes.login]:{
			userId: "",
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
			state.values[AccountsCallTypes.login] = {
				...initialState.values[AccountsCallTypes.login],
			};
		},
	},
	extraReducers: {
		[login.pending]: (state) => {
			state.status[AccountsCallTypes.login] = CallStatus.loading;
		},
		[login.fulfilled]: (state, action) => {
			state.status[AccountsCallTypes.login] = CallStatus.done;
			state.values[AccountsCallTypes.login] = action.payload;
		},
		[login.rejected]: (state, action) => {
			state.status[AccountsCallTypes.login] = CallStatus.done;
			state.error[AccountsCallTypes.login] = action.payload;
		},
	},
});

export const isAdminSelector = appState =>
	appState.accounts.values[AccountsCallTypes.login].roles
		.some(r => r.startsWith(UserRoleDef.ADMIN));

export const hasAnyRolesSelector = (requiredRoles) => (appState) => {
	if(!requiredRoles || requiredRoles.length < 1) return true;
	const userRoles = appState.accounts.values[AccountsCallTypes.login].roles;
	if(userRoles.some(r => r.startsWith(UserRoleDef.ADMIN))) {
		return true;
	}
	for (const role of requiredRoles) {
		if(userRoles.some(r => r.startsWith(role))) {
			return true;
		}
	}
	return false;
};

export const currentUserSelector = appState =>
	appState.accounts.values[AccountsCallTypes.login];

export const logout = slice.actions.logout;

export default slice.reducer;