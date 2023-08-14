import { AxiosPromise } from "axios";
import { defaultWebClient as webClient } from "./api";
import {
	LoginCredentials,
	LoggedInUser,
	UserCreationInfo,
	User,
	SubjectUserKeyItem,
	RoledUser,
	ExistenceCheckParams,
	UserBase
} from "../Types/user_types";
import { PageableParams } from "../Types/pageable_types";

export { webClient };


export const login = async ({
	username,
	password,
}: LoginCredentials) => {
	const formData = new window.FormData();
	formData.append("username", username);
	formData.append("password", password);
	const response = await webClient.post<LoggedInUser>(
		"accounts/open",
		formData
	);
	webClient.defaults.headers.common["Authorization"] =
	`Bearer ${response.data.access_token}`;
	return response.data;
};

export const login_with_cookie = async () => {
	const response = await webClient.post<LoggedInUser>("accounts/open_cookie");
	webClient.defaults.headers.common["Authorization"] =
		`Bearer ${response.data.access_token}`;
	return response.data;
};

export const createAccount = async (
	{ values }: { values: UserCreationInfo}
) => {
	const response = await webClient.post<User>("accounts/new", values);
	return response.data;
};

export const checkValues = async (
	{ values }: { values: ExistenceCheckParams}
) => {
	const response = await webClient.get("accounts/check", {
		params: values,
	});
	return response.data;
};

export const fetchUser = async ({ subjectUserKey }: SubjectUserKeyItem) => {
	const response = await webClient.get(`accounts/account/${subjectUserKey}`);
	return response.data;
};

export const fetchUserList = async ({ params }: { params: PageableParams}) => {
	const response = await webClient.get("accounts/list", {
		params: params,
	});
	return response.data;
};

export const searchUsers = async ({ params }: { params: PageableParams}) => {
	const response = await webClient.get("accounts/search", {
		params: params,
	});
	return response.data;
};

export const updateUserRoles = async ({ id, roles }: RoledUser) => {
	const response = await webClient.put(`accounts/update-roles/${id}`,
		roles
	);
	return response.data;
};

export const updateAccountBasic = async ({ subjectUserKey, data }) => {
	const response = await webClient.put(
		`accounts/account/${subjectUserKey}`,
		data
	);
	return response.data;
};

export const updatePassword = async ({
	subjectUserKey,
	oldPassword,
	newPassword,
}) => {
	const response = await webClient.put(
		`accounts/update-password/${subjectUserKey}`,
		{
			oldPassword,
			newPassword,
		}
	);
	return response.data;
};

export const fetchSiteRuleUsers = async ({ params }) => {
	const url = "/site-roles/user_list";
	const response = await webClient.get(url, {
		params: params,
	});
	return response.data;
};

export const addSiteUserRule = async ({ subjectUserKey, rule }) => {
	const url = `accounts/site-roles/user_role/${subjectUserKey}`;
	const response = await webClient.post(url, rule);
	return response.data;
};

export const removeSiteUserRule = async ({ subjectUserKey, params }) => {
	const url = `accounts/site-roles/user_role/${subjectUserKey}`;
	const response = await webClient.delete(url, {
		params: params,
	});
	return response.data;
};