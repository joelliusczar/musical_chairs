import { defaultWebClient as webClient } from "./api";

export const AccountsCallTypes = {
	login: "login",
};


export const login = async ({
	username,
	password,
	logout,
	responseInterceptorKey,
}) => {
	const formData = new window.FormData();
	formData.append("username", username);
	formData.append("password", password);
	const response = await webClient.post("accounts/open", formData);
	webClient.defaults.headers.common["Authorization"] =
	`Bearer ${response.data.access_token}`;
	if (!responseInterceptorKey) {
		responseInterceptorKey = webClient.interceptors.response.use(
			null,
			(err) => {
				if ("x-authexpired" in (err?.response?.headers || {})) {
					logout();
				}
				return Promise.reject(err);
			});
	}
	return { data: response.data, interceptor: responseInterceptorKey };
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






