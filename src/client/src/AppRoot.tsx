import React, { createRef, useState } from "react";
import { css } from "@emotion/react";
import {
	ThemeProvider,
	Button,
	Tooltip,
} from "@mui/material";
import { AppRoutes, NavMenu } from "./Components/Navigation/NavRoutes";
import { theme } from "./style_config";
import { SnackbarProvider } from "notistack";
import { UserMenu } from "./Components/Accounts/UserMenu";
import {
	useCurrentUser,
	useLoginPrompt,
} from "./Context_Providers/AuthContext/AuthContext";
import {
	AuthContextProvider,
} from "./Context_Providers/AuthContext/AuthContextProvider";
import {
	AppContextProvider,
} from "./Context_Providers/AppContext/AppContextProvider";
import { buildTimespanMsg, secondsToTuple } from "./Helpers/time_helper";
import { cookieToObject } from "./Helpers/browser_helpers";


const AppTrunk = () => {
	const currentUser = useCurrentUser();
	const openLoginPrompt = useLoginPrompt();
	const [logginTooltipMsg, setLogginTooltipMsg] = useState("");
	const cookieObj = cookieToObject(document.cookie);
	const usernameCookie = decodeURIComponent(cookieObj["username"] || "");

	const displayNameCookie = decodeURIComponent(
		cookieObj["displayname"] || ""
	) || usernameCookie;

	const loggedInTimespan = () => {
		const timeTuple = secondsToTuple(
			(Date.now() / 1000) - currentUser.login_timestamp
		);
		return `Logged in for ${buildTimespanMsg(
			timeTuple
		)}`;
	};

	const styles = {
		parent: css`
			display: grid;
			grid-template-columns: 240px 1fr;
			grid-template-rows: 1fr;
		`,
		content: css`
			padding-inline-start: 25px;
		`,
		header: css`
			padding-inline-start: 25px;
			background-color: #0A5;
			color: #FFF;
			grid-column: 1 / 3
			`,
		header_h1: css`
			font-family: "Monoton", sans-serif;
			font-weight: 400;
			font-style: normal;
			display: inline;
		`,
		menu_icon: css`
			margin-right: 10px;
		`,
		floating_menu: css`
			grid-column: 1
		`,
	};



	return (
		<div css={styles.parent}>
			<div css={styles.header}>
				<h1 css={styles.header_h1}>Musical Chairs</h1>
				 	{!(!!currentUser.username || !!displayNameCookie) ? <Button
		 				color="inherit"
		 				onClick={() => openLoginPrompt()}
		 			>
		 				Login
		 			</Button> :
		 				<>
						<Tooltip
		 						title={logginTooltipMsg}
		 						onOpen={() => setLogginTooltipMsg(loggedInTimespan())}
		 					>
		 						<UserMenu
		 							btnLabel={currentUser.username || displayNameCookie}
		 						/>
		 					</Tooltip>
		 				</>
		 			}
			</div>
			<div>
				<NavMenu />
			</div>
			<div>
				<AppRoutes />
			</div>
		</div>
	);
};

function AppRoot() {
	const notistackRef = createRef<SnackbarProvider>();

	return (
		<SnackbarProvider
			ref={notistackRef}
			onClick={() => notistackRef?.current?.closeSnackbar()}
		>
			<ThemeProvider theme={theme}>
				<AuthContextProvider>
					<AppContextProvider>
						<AppTrunk />
					</AppContextProvider>
				</AuthContextProvider>
			</ThemeProvider>
		</SnackbarProvider>
	);
}

export default AppRoot;
