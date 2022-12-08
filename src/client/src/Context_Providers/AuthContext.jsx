import React, {
	createContext,
	useReducer,
	useContext,
	useMemo,
	useState,
} from "react";
import PropTypes from "prop-types";
import { login } from "../API_Calls/userCalls";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Components/Shared/waitingReducer";
import { UserRoleDef } from "../constants";
import { formatError } from "../Helpers/error_formatter";
import { useSnackbar } from "notistack";

const loggedOut = {
	userId: "",
	username: "",
	roles: [],
	access_token: "",
	lifetime: 0,
};

const loggedOutState = {
	...initialState,
	data: loggedOut,
};

const AuthContext = createContext();

export const AuthContextProvider = (props) => {
	const { children } = props;
	const [state, dispatch] = useReducer(
		waitingReducer(),
		loggedOutState
	);
	const [ responseInterceptorKey, setResponseInterceptorKey] = useState();

	const contextValue = useMemo(() => ({
		state,
		dispatch,
		responseInterceptorKey,
		setResponseInterceptorKey,
	}), [state, responseInterceptorKey, setResponseInterceptorKey]);

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
		responseInterceptorKey,
		setResponseInterceptorKey,
	} = useContext(AuthContext);
	const { enqueueSnackbar } = useSnackbar();
	const _logout = () => {
		dispatch(dispatches.reset(loggedOutState));
		enqueueSnackbar("Logging out.");
	};
	const _login = async (username, password) => {
		try {
			dispatch(dispatches.started());
			const { data, interceptor } = await login({
				username,
				password,
				logout: _logout,
				responseInterceptorKey,
			});
			setResponseInterceptorKey(interceptor);
			dispatch(dispatches.done(data));
		}
		catch(err) {
			dispatch(dispatches.failed(formatError(err)));
			throw err;
		}
	};
	return [_login, _logout];
};