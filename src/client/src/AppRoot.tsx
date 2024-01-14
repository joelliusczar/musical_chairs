import React, { createRef, useState } from "react";
import "./App.css";
import {
	AppBar,
	Drawer,
	ThemeProvider,
	Typography,
	Box,
	Toolbar,
	Button,
	Tooltip,
} from "@mui/material";
import { AppRoutes, NavMenu } from "./Components/Navigation/NavRoutes";
import { theme, drawerWidth } from "./style_config";
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


function AppTrunk() {
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


	return (
		<Box sx={{ display: "flex" }}>
			<AppBar
				color="primary"
				position="fixed"
				sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px`}}
			>
				<Toolbar>
					<Typography variant="h1">Musical Chairs</Typography>
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
				</Toolbar>
			</AppBar>
			<Drawer
				variant="permanent"
				anchor="left"
				sx={{
					width: drawerWidth,
					flexShrink: 0,
				}}
				classes={{
					paper: "drawer",
				}}
			>
				<NavMenu />
			</Drawer>
			<Box
				component="main"
				sx={{ flexFlow: 1, p: 3}}
			>
				<Toolbar />
				<AppRoutes />
			</Box>
		</Box>
	);
}

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
