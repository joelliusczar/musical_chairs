import React, { useState, createRef } from "react";
import "./App.css";
import {
	AppBar,
	Drawer,
	ThemeProvider,
	Typography,
	Box,
	Toolbar,
	Button,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import { AppRoutes, NavMenu } from "./Components/Navigation/NavRoutes";
import { theme, drawerWidth } from "./style_config";
import { SnackbarProvider } from "notistack";
import { UserMenu } from "./Components/Accounts/UserMenu";
import {
	AuthContextProvider,
	useCurrentUser,
	useLoginPrompt,
} from "./Context_Providers/AuthContext";
import {
	AppContextProvider,
} from "./Context_Providers/AppContextProvider";

export const useStyles = makeStyles((theme) => ({
	drawerPaper: {
		width: drawerWidth,
	},
	offset: theme.mixins.toolbar,
}));

function AppTrunk() {
	const classes = useStyles();
	const [menuAnchor, setMenuAnchor ] = useState(null);
	const currentUser = useCurrentUser();
	const openLoginPrompt = useLoginPrompt();

	return (
		<Box sx={{ display: "flex" }}>
			<AppBar
				color="primary"
				position="fixed"
				sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px`}}
			>
				<Toolbar>
					<Typography variant="h1">Musical Chairs</Typography>
					{!currentUser.username ? <Button
						color="inherit"
						onClick={() => openLoginPrompt()}
					>
						Login
					</Button> :
						<>
							<UserMenu
								anchorEl={menuAnchor}
								btnLabel={currentUser.username}
								closeMenu={() => setMenuAnchor(null)}
							/>
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
					paper: classes.drawerPaper,
				}}
			>
				<NavMenu />
			</Drawer>
			<Box
				component="main"
				sx={{ flexFlow: 1, p: 3}}
			>
				<Box className={classes.offset} />
				<AppRoutes />
			</Box>
		</Box>
	);
}

function AppRoot() {
	const notistackRef = createRef();

	return (
		<SnackbarProvider
			ref={notistackRef}
			onClick={() => notistackRef.current.closeSnackbar()}
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
