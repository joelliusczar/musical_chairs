import React, {
	useMemo,
	useState,
	useEffect,
	useCallback,
} from "react";
import PropTypes from "prop-types";
import { loginWithCookie, webClient } from "../../API_Calls/userCalls";
import {
	useDataWaitingReducer,
	dataDispatches as dispatches,
} from "../../Reducers/dataWaitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { useSnackbar } from "notistack";
import { LoginModal } from "../../Components/Accounts/AccountsLoginModal";
import { BrowserRouter } from "react-router-dom";
import {
	AuthContext,
	loggedOutState,
} from "./AuthContext";






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
		
		dispatch(dispatches.set({
			...loggedOutState.data,
			username: loggedInUsername,
		}));
		clearCookies();
		enqueueSnackbar("ending session.");
	},[dispatch, enqueueSnackbar, loggedInUsername]);


	const logout = useCallback(() => {
		dispatch(dispatches.set(loggedOutState.data));
		clearCookies();
		webClient.defaults.headers.common["Authorization"] = null;
		webClient.interceptors.response.clear();
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
				webClient.defaults.headers.common["Authorization"] = null;
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


