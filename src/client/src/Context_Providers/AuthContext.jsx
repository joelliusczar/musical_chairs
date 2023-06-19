import React, {
	createContext,
	useReducer,
	useContext,
	useMemo,
	useState,
	useEffect,
	useCallback,
} from "react";
import PropTypes from "prop-types";
import { login, login_with_cookie, webClient } from "../API_Calls/userCalls";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Components/Shared/waitingReducer";
import { UserRoleDef } from "../constants";
import { formatError } from "../Helpers/error_formatter";
import {
	anyConformsToRule,
	anyConformsToAnyRule,
} from "../Helpers/rule_helpers";
import { useSnackbar } from "notistack";
import { LoginModal } from "../Components/Accounts/AccountsLoginModal";
import { BrowserRouter } from "react-router-dom";


const loggedOut = {
	username: "",
	roles: [],
	access_token: "",
	lifetime: 0,
};

const loggedOutState = {
	...initialState,
	data: loggedOut,
};

const expireCookie = (name) => {
	document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;";
};


const clearCookies = () => {
	expireCookie("username");
	expireCookie("displayName");
	expireCookie("access_token");
};



export const AuthContext = createContext();

export const AuthContextProvider = (props) => {
	const { children } = props;
	const [state, dispatch] = useReducer(
		waitingReducer(),
		loggedOutState
	);

	const [loginOpen, setLoginOpen ] = useState(false);
	const [loginPromptCancelAction, setLoginPromptCancelAction] = useState();

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
		dispatch(dispatches.reset(loggedOutState));
		clearCookies();
		enqueueSnackbar("Logging out.");
	},[dispatch, enqueueSnackbar]);

	const openLoginPrompt = useCallback((onCancel) => {
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
		if (loggedInUsername) return;
		const kvps = document.cookie.split(";");
		const username = decodeURIComponent(
			kvps.find(kvp => kvp.startsWith("username"))?.split("=")[1] || ""
		);

		const displayName = decodeURIComponent(
			kvps.find(kvp => kvp.startsWith("displayName"))
				?.split("=")[1] || username
		);

		if(!document.cookie) return;
		dispatch(dispatches.assign({username, displayName}));
		const loginCall = async () => {
			try {
				const data = await login_with_cookie();
				setupAuthExpirationAction();
				dispatch(dispatches.done(data));
			}
			catch (err) {
				enqueueSnackbar(formatError(err), { variant: "error" });
			}
		};
		loginCall();
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

export const useHasAnyRoles = (requiredRoles) => {
	if(!requiredRoles || requiredRoles.length < 1) return true;
	const { state: { data } } = useContext(AuthContext);
	const userRoles = data?.roles;

	if (anyConformsToRule(userRoles, UserRoleDef.ADMIN)) {
		return true;
	}

	if (anyConformsToAnyRule(userRoles, requiredRoles)) {
		return true;
	}
	return false;
};

export const useLogin = () => {
	const {
		dispatch,
		setupAuthExpirationAction,
		logout,
	} = useContext(AuthContext);

	const _login = async (username, password) => {
		try {
			dispatch(dispatches.started());
			const data = await login({
				username,
				password,
			});
			setupAuthExpirationAction();
			dispatch(dispatches.done(data));
		}
		catch(err) {
			dispatch(dispatches.failed(formatError(err)));
			throw err;
		}
	};
	return [_login, logout];
};

export const useLoginPrompt = () => {
	const {
		openLoginPrompt,
	} = useContext(AuthContext);

	return openLoginPrompt;
};

export const useAuthViewStateChange = (dispatch) => {
	const currentUser = useCurrentUser();

	useEffect(() => {
		if(currentUser.username) {
			dispatch(dispatches.restart());
		}
	},[currentUser.username, dispatch]);
};