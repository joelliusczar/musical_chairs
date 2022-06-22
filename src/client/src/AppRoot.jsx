import React, { useState } from "react";
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
import { BrowserRouter } from "react-router-dom";
import { apiAddress } from "./constants";
import { Provider } from "react-redux";
import store from "./reducers";
import { theme, drawerWidth } from "./style_config";
import { LoginModal } from "./Components/Accounts/AccountsLoginModal";
import { SnackbarProvider } from "notistack";
import { UserMenu } from "./Components/Accounts/UserMenu";
import { AuthContextProvider } from "./Components/Accounts/AuthContext";
import { useCurrentUser } from "./Components/Accounts/AuthContext";

export const useStyles = makeStyles(() => ({
	drawerPaper: {
		width: drawerWidth,
	},
}));

function AppTrunk() {
	const classes = useStyles();
	const [loginOpen, setLoginOpen ] = useState(false);
	const [menuAnchor, setMenuAchor ] = useState(null);
	const currentUser = useCurrentUser();

	const openUserMenu = (e) => {
		setMenuAchor(e.currentTarget);
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
					{!currentUser.username ? <Button
						color="inherit"
						onClick={() => setLoginOpen(true)}
					>
						Login
					</Button> :
						<>
							<Button
								color="inherit"
								onClick={openUserMenu}
							>
								{currentUser.username}
							</Button>
							<UserMenu
								anchorEl={menuAnchor}
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
				<Typography variant="h1">{apiAddress}</Typography>
				<AppRoutes />
			</Box>
			<LoginModal open={loginOpen} setOpen={setLoginOpen} />
		</Box>
	);
}

function AppRoot() {
	return (
		<Provider store={store}>
			<AuthContextProvider>
				<ThemeProvider theme={theme}>
					<SnackbarProvider>
						<BrowserRouter basename="/">
							<AppTrunk />
						</BrowserRouter>
					</SnackbarProvider>
				</ThemeProvider>
			</AuthContextProvider>
		</Provider>
	);
}

export default AppRoot;
