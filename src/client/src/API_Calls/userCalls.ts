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


export const login = ({
	username,
	password,
}: LoginCredentials) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const formData = new window.FormData();
			formData.append("username", username);
			formData.append("password", password);
			const response = await webClient.post<LoggedInUser>(
				"accounts/open",
				formData,
				{ signal: abortController.signal }
			);
			webClient.defaults.headers.common["Authorization"] =
			`Bearer ${response.data.access_token}`;
			return response.data;
		},
	};
};

export const loginWithCookie = () => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.post<LoggedInUser>(
				"accounts/open_cookie",
				null,
				{ signal: abortController.signal }
			);
			webClient.defaults.headers.common["Authorization"] =
				`Bearer ${response.data.access_token}`;
			return response.data;
		},
	};
};

export const createAccount = ({ values }: { values: UserCreationInfo}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.post<User>(
				"accounts/new",
				values,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const checkValues = ({ values }: { values: ExistenceCheckParams}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<Flags<ExistenceCheckParams>>(
				"accounts/check", {
					params: values,
					signal: abortController.signal,
				});
			return response.data;
		},
	};
};

export const fetchUser = ({ subjectuserkey }: SubjectUserKeyItem) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<User>(
				`accounts/account/${subjectuserkey}`,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const fetchUserList = ({ params }: { params: PageableParams}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<TableData<User>>(
				"accounts/list",
				{
					params: params,
					signal: abortController.signal,
				}
			);
			return response.data;
		},
	};
};

export const searchUsers = ({ params }: { params: PageableParams}) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.get<User[]>("accounts/search", {
				params: params,
				signal: abortController.signal,
			});
			return response.data;
		},
	};
};

export const updateUserRoles = ({ id, roles }: RoledUser) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.put<User>(
				`accounts/update-roles/${id}`,
				roles,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const updateAccountBasic = (
	{ subjectuserkey, data }: UserBasicUpdateApiParams
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.put<User>(
				`accounts/account/${subjectuserkey}`,
				data,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const updatePassword = ({
	subjectuserkey,
	oldpassword,
	newpassword,
}: SubjectPasswordUpdate) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const response = await webClient.put<boolean>(
				`accounts/update-password/${subjectuserkey}`,
				{
					oldpassword,
					newpassword,
				},
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const addSiteUserRule = (
	{
		subjectuserkey,
		rule,
	}: SubjectUserRoleAddition
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `accounts/site-roles/user_role/${subjectuserkey}`;
			const response = await webClient.post<ActionRule>(
				url,
				rule,
				{ signal: abortController.signal }
			);
			return response.data;
		},
	};
};

export const removeSiteUserRule = (
	{ subjectuserkey, rulename }: SubjectUserRoleDeletion
) => {
	const abortController = new AbortController();
	return {
		abortController: abortController,
		call: async () => {
			const url = `accounts/site-roles/user_role/${subjectuserkey}`;
			const response = await webClient.delete<void>(url, {
				params: {
					rulename,
					signal: abortController.signal,
				},
			});
			return response.data;
		},
	};
};
