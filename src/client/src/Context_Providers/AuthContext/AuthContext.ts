import React, {
	createContext,
	useContext,
	useEffect,
	useCallback,
} from "react";
import { login } from "../../API_Calls/userCalls";
import {
	DataActionPayload,
	dataDispatches as dispatches,
} from "../../Reducers/dataWaitingReducer";
import { UserRoleDef } from "../../constants";
import { formatError } from "../../Helpers/error_formatter";
import {
	anyConformsToRule,
	anyConformsToAnyRule,
} from "../../Helpers/rule_helpers";
import { LoggedInUser } from "../../Types/user_types";
import {
	WaitingTypes,
} from "../../Types/reducerTypes";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import { getUsernameCookie } from "../../Helpers/browser_helpers";

export type AuthContextType = {
	state: RequiredDataStore<LoggedInUser>,
	dispatch: React.Dispatch<DataActionPayload<LoggedInUser>>,
	setupAuthExpirationAction: () => void
	logout: () => void,
	partialLogout: () => void,
	openLoginPrompt: (onCancel?: () => void) => void
};

const loggedOut = {
	username: "",
	roles: [],
	access_token: "",
	lifetime: 0,
	login_timestamp: 0,
};

type loginFnType = (username: string, password: string) => void;

export const loggedOutState = new RequiredDataStore<LoggedInUser>(loggedOut);

export const AuthContext = createContext<AuthContextType>({
	state: loggedOutState,
	dispatch: ({}) => {},
	setupAuthExpirationAction: () => {},
	logout: () => {},
	partialLogout: () => {},
	openLoginPrompt: () => {},
});

export const useCurrentUser = () => {
	const { state: { data } } = useContext(AuthContext);
	return data;
};

export const useHasAnyRoles = (requiredRoleNames: string[]) => {
	const { state: { data } } = useContext(AuthContext);
	if(!requiredRoleNames || requiredRoleNames.length < 1) return true;
	const userRoles = data?.roles;

	if (!userRoles) {
		return false;
	}
	if (anyConformsToRule(userRoles, UserRoleDef.ADMIN)) {
		return true;
	}

	if (anyConformsToAnyRule(userRoles, requiredRoleNames)) {
		return true;
	}
	return false;
};

export const useLogin: () => [loginFnType, () => void] = () => {
	const {
		dispatch,
		setupAuthExpirationAction,
		logout,
	} = useContext(AuthContext);

	const _login = useCallback( async (username: string, password: string) => {
		try {
			const requestObj = login({
				username,
				password,
			});
			dispatch(dispatches.started());
			const data = await requestObj.call();
			setupAuthExpirationAction();
			dispatch(dispatches.done(data));
		}
		catch(err) {
			dispatch(dispatches.failed(formatError(err)));
			throw err;
		}
	},[dispatch, setupAuthExpirationAction]);
	return [_login, logout];
};

export const useLoginPrompt = () => {
	const {
		openLoginPrompt,
	} = useContext(AuthContext);

	return openLoginPrompt;
};

export const useAuthViewStateChange = (
	dispatch: (action: { type: WaitingTypes.restart }) => void
) => {
	const currentUser = useCurrentUser();
	const usernameCookie = getUsernameCookie(document.cookie);
	const username = (currentUser.username || usernameCookie)?.trim();

	useEffect(() => {
		if(username) {
			dispatch({ type: WaitingTypes.restart });
		}
	},[username, dispatch]);
};