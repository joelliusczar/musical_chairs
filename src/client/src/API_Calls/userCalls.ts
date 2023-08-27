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
	SubjectPasswordUpdate,
	UserBasicUpdateApiParams,
	SubjectUserRoleAddition,
	SubjectUserRoleDeletion,
	ActionRule,
} from "../Types/user_types";
import { PageableParams, TableData } from "../Types/pageable_types";
import { Flags } from "../Types/generic_types";
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
	const response = await webClient.get<Flags<ExistenceCheckParams>>(
		"accounts/check", {
			params: values,
		});
	return response.data;
};

export const fetchUser = async ({ subjectUserKey }: SubjectUserKeyItem) => {
	const response = await webClient.get<User>(
		`accounts/account/${subjectUserKey}`
	);
	return response.data;
};

export const fetchUserList = async ({ params }: { params: PageableParams}) => {
	const response = await webClient.get<TableData<User>>(
		"accounts/list",
		{
			params: params,
		}
	);
	return response.data;
};

export const searchUsers = async ({ params }: { params: PageableParams}) => {
	const response = await webClient.get<User[]>("accounts/search", {
		params: params,
	});
	return response.data;
};

export const updateUserRoles = async ({ id, roles }: RoledUser) => {
	const response = await webClient.put<User>(`accounts/update-roles/${id}`,
		roles
	);
	return response.data;
};

export const updateAccountBasic = async (
	{ subjectUserKey, data }: UserBasicUpdateApiParams
) => {
	const response = await webClient.put<User>(
		`accounts/account/${subjectUserKey}`,
		data
	);
	return response.data;
};

export const updatePassword = async ({
	subjectUserKey,
	oldPassword,
	newPassword,
}: SubjectPasswordUpdate) => {
	const response = await webClient.put<boolean>(
		`accounts/update-password/${subjectUserKey}`,
		{
			oldPassword,
			newPassword,
		}
	);
	return response.data;
};

export const addSiteUserRule = async (
	{
		subjectUserKey,
		rule,
	}: SubjectUserRoleAddition
) => {
	const url = `accounts/site-roles/user_role/${subjectUserKey}`;
	const response = await webClient.post<ActionRule>(url, rule);
	return response.data;
};

export const removeSiteUserRule = async (
	{ subjectUserKey, ruleName }: SubjectUserRoleDeletion
) => {
	const url = `accounts/site-roles/user_role/${subjectUserKey}`;
	const response = await webClient.delete<void>(url, {
		params: {
			ruleName,
		},
	});
	return response.data;
};