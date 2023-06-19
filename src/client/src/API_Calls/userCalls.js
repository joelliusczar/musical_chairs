import { defaultWebClient as webClient } from "./api";

export { webClient };


export const login = async ({
	username,
	password,
}) => {
	const formData = new window.FormData();
	formData.append("username", username);
	formData.append("password", password);
	const response = await webClient.post(
		"accounts/open",
		formData
	);
	webClient.defaults.headers.common["Authorization"] =
	`Bearer ${response.data.access_token}`;
	return response.data;
};

export const login_with_cookie = async () => {
	const response = await webClient.post("accounts/open_cookie");
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

export const fetchUser = async ({ userKey }) => {
	const response = await webClient.get(`accounts/account/${userKey}`);
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

export const updateAccountBasic = async ({ userKey, data }) => {
	const response = await webClient.put(`accounts/account/${userKey}`, data);
	return response.data;
};

export const updatePassword = async ({
	userKey,
	oldPassword,
	newPassword,
}) => {
	const response = await webClient.put(`accounts/update-password/${userKey}`, {
		oldPassword,
		newPassword,
	});
	return response.data;
};





