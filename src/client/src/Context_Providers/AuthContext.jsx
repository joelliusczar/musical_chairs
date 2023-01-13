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
import { login, login_with_cookie } from "../API_Calls/userCalls";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Components/Shared/waitingReducer";
import { UserRoleDef } from "../constants";
import { formatError } from "../Helpers/error_formatter";
import { useSnackbar } from "notistack";

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
	document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:01 GMT;";
};


const AuthContext = createContext();

export const AuthContextProvider = (props) => {
	const { children } = props;
	const [state, dispatch] = useReducer(
		waitingReducer(),
		loggedOutState
	);
	const [ , setResponseInterceptorKey] = useState();
	const { enqueueSnackbar } = useSnackbar();
	const loggedInUsername = state.data.username;

	const logout = useCallback(() => {
		dispatch(dispatches.reset(loggedOutState));
		expireCookie("username");
		expireCookie("displayName");
		expireCookie("access_token");
		enqueueSnackbar("Logging out.");
	},[dispatch, enqueueSnackbar]);

	const contextValue = useMemo(() => ({
		state,
		dispatch,
		setResponseInterceptorKey,
		logout,
	}), [state, setResponseInterceptorKey]);

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
		const asyncCall = async () => {
			try {
				const data = await login_with_cookie(
					logout,
					setResponseInterceptorKey
				);
				dispatch(dispatches.done(data));
			}
			catch (err) {
				enqueueSnackbar(formatError(err), { variant: "error" });
			}
		};
		asyncCall();
	},[
		dispatch,
		setResponseInterceptorKey,
		logout,
		enqueueSnackbar,
		loggedInUsername,
	]);

	return (
		<AuthContext.Provider value={contextValue}>
			{children}
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
	if(userRoles?.some(r => r.startsWith(UserRoleDef.ADMIN))) {
		return true;
	}
	for (const role of requiredRoles) {
		if(userRoles?.some(r => r.startsWith(role))) {
			return true;
		}
	}
	return false;
};

export const useLogin = () => {
	const {
		dispatch,
		setResponseInterceptorKey,
		logout,
	} = useContext(AuthContext);

	const _login = async (username, password) => {
		try {
			dispatch(dispatches.started());
			const data = await login({
				username,
				password,
				logout: logout,
				setResponseInterceptorKey,
			});
			dispatch(dispatches.done(data));
		}
		catch(err) {
			dispatch(dispatches.failed(formatError(err)));
			throw err;
		}
	};
	return [_login, logout];
};