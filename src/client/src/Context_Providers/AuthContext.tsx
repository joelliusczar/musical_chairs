import React, {
	createContext,
	useContext,
	useMemo,
	useState,
	useEffect,
	useCallback,
} from "react";
import PropTypes from "prop-types";
import { login, loginWithCookie, webClient } from "../API_Calls/userCalls";
import {
	dispatches,
} from "../Reducers/waitingReducer";
import {
	useDataWaitingReducer,
} from "../Reducers/dataWaitingReducer";
import { UserRoleDef } from "../constants";
import { formatError } from "../Helpers/error_formatter";
import {
	anyConformsToRule,
	anyConformsToAnyRule,
} from "../Helpers/rule_helpers";
import { useSnackbar } from "notistack";
import { LoginModal } from "../Components/Accounts/AccountsLoginModal";
import { BrowserRouter } from "react-router-dom";
import { LoggedInUser } from "../Types/user_types";
import {
	ActionPayload,
} from "../Reducers/types/reducerTypes";
import { RequiredDataStore } from "../Reducers/reducerStores";

type loginFnType = (username: string, password: string) => void;

const loggedOut = {
	username: "",
	roles: [],
	access_token: "",
	lifetime: 0,
	login_timestamp: 0,
};

const loggedOutState = new RequiredDataStore<LoggedInUser>(loggedOut);

const expireCookie = (name: string) => {
	const cookieStr = name + 
		"=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;SameSite=None;";
	document.cookie = cookieStr;
};


const clearCookies = () => {
	expireCookie("username");
	expireCookie("displayname");
	expireCookie("access_token");
	expireCookie("login_timestamp");
};

type AuthContextType = {
	state: RequiredDataStore<LoggedInUser>,
	dispatch: React.Dispatch<ActionPayload<LoggedInUser, LoggedInUser>>,
	setupAuthExpirationAction: () => void
	logout: () => void,
	partialLogout: () => void,
	openLoginPrompt: (onCancel?: () => void) => void
}


export const AuthContext = createContext<AuthContextType>({
	state: loggedOutState,
	dispatch: ({}) => {},
	setupAuthExpirationAction: () => {},
	logout: () => {},
	partialLogout: () => {},
	openLoginPrompt: () => {},
});

export const AuthContextProvider = (props: { children: JSX.Element }) => {
	const { children } = props;
	const [state, dispatch] = useDataWaitingReducer(
		loggedOutState
	);

	const [loginOpen, setLoginOpen ] = useState(false);
	const [loginPromptCancelAction, setLoginPromptCancelAction] =
		useState<(() => void) | null>(null);

	const { enqueueSnackbar } = useSnackbar();
	const loggedInUsername = state.data.username;

	const partialLogout = useCallback(() => {
		dispatch(dispatches.reset({
			...loggedOutState.data,
			username: loggedInUsername,
		}));
		clearCookies();
		enqueueSnackbar("Logging out.");
	},[dispatch, enqueueSnackbar, loggedInUsername]);


	const logout = useCallback(() => {
		dispatch(dispatches.reset(loggedOutState.data));
		clearCookies();
		enqueueSnackbar("Logging out.");
	},[dispatch, enqueueSnackbar]);

	const openLoginPrompt = useCallback((onCancel?: () => void) => {
		setLoginOpen(true);
		if (onCancel) {
			setLoginPromptCancelAction(() => onCancel);
		}
		else {
			setLoginPromptCancelAction(null);
		}
	},[setLoginOpen]);


	const setupAuthExpirationAction = useCallback(() => {

		//want closure references to be updating so we're clearing rather
		//than reusing
		webClient.interceptors.response.clear();

		webClient.interceptors.response.use(
			null,
			(err) => {
				if ("x-authexpired" in (err?.response?.headers || {})) {
					partialLogout();
					openLoginPrompt(logout);
				}
				return Promise.reject(err);
			}
		);

	}, [partialLogout, openLoginPrompt, logout]);

	useEffect(() => {
		setupAuthExpirationAction();
	},[setupAuthExpirationAction]);


	const contextValue = useMemo(() => ({
		state,
		dispatch,
		setupAuthExpirationAction,
		logout,
		partialLogout,
		openLoginPrompt,
	}), [
		state,
		dispatch,
		setupAuthExpirationAction,
		logout,
		partialLogout,
		openLoginPrompt,
	]);

	useEffect(() => {
		const requestObj = loginWithCookie();
		if (loggedInUsername) return;

		if(!document.cookie) return;

		const loginCall = async () => {
			try {
				const data = await requestObj.call();
				setupAuthExpirationAction();
				dispatch(dispatches.done(data));
			}
			catch (err) {
				enqueueSnackbar(formatError(err), { variant: "error" });
			}
		};
		loginCall();
		return () => requestObj.abortController.abort();
	},[
		dispatch,
		setupAuthExpirationAction,
		enqueueSnackbar,
		loggedInUsername,
	]);

	return (
		<AuthContext.Provider value={contextValue}>
			<BrowserRouter basename="/">
				<>
					{children}
				</>
				<LoginModal
					open={loginOpen}
					setOpen={setLoginOpen}
					onCancel={loginPromptCancelAction}
				/>
			</BrowserRouter>
		</AuthContext.Provider>
	);

};

AuthContextProvider.propTypes = {
	children: PropTypes.oneOfType([
		PropTypes.arrayOf(PropTypes.node),
		PropTypes.node,
	]).isRequired,
};

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

export const useAuthViewStateChange = <T, U=T>(
	dispatch: (action:ActionPayload<T,U>) => void
) => {
	const currentUser = useCurrentUser();

	useEffect(() => {
		if(currentUser.username) {
			dispatch(dispatches.restart());
		}
	},[currentUser.username, dispatch]);
};