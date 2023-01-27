import { defaultWebClient as webClient } from "./api";


const setupAuthExpirationAction = (logout, setResponseInterceptorKey) => {
	setResponseInterceptorKey(previousKey => {
		if(!previousKey) {
			const responseInterceptorKey = webClient.interceptors.response.use(
				null,
				(err) => {
					if ("x-authexpired" in (err?.response?.headers || {})) {
						logout();
					}
					return Promise.reject(err);
				});
			return responseInterceptorKey;
		}
		return previousKey;
	});
};


export const login = async ({
	username,
	password,
	logout,
	setResponseInterceptorKey,
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
	setupAuthExpirationAction(logout, setResponseInterceptorKey);
	return response.data;
};

export const login_with_cookie = async (logout, setResponseInterceptorKey) => {
	const response = await webClient.post("accounts/open_cookie");
	webClient.defaults.headers.common["Authorization"] =
		`Bearer ${response.data.access_token}`;
	setupAuthExpirationAction(logout, setResponseInterceptorKey);

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

export const fetchUser = async ({ id, username }) => {
	const response = await webClient.get("accounts", {
		params: {
			userId: id,
			username,
		},
	});
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

export const updateAccountBasic = async ({ id, username, data }) => {
	const response = await webClient.put("accounts", data, {
		params: {
			userId: id,
			username,
		},
	});
	return response.data;
};

export const updatePassword = async ({
	id,
	username,
	oldPassword,
	newPassword,
}) => {
	const response = await webClient.put("accounts/update-password/", {
		oldPassword,
		newPassword,
	}, {
		params: {
			userId: id,
			username,
		},
	});
	return response.data;
};





