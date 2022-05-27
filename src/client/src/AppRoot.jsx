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

export const useStyles = makeStyles(() => ({
	drawerPaper: {
		width: drawerWidth,
	},
}));

function AppTrunk() {
	const classes = useStyles();
	const [loginOpen, setLoginOpen ] = useState(false);

	return (
		<Box sx={{ display: "flex" }}>
			<AppBar
				color="primary"
				position="fixed"
				sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px`}}
			>
				<Toolbar>
					<Typography variant="h1">Musical Chairs</Typography>
					<Button
						color="inherit"
						onClick={() => setLoginOpen(true)}
					>
						Login
					</Button>
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
			<ThemeProvider theme={theme}>
				<SnackbarProvider>
					<BrowserRouter basename="/">
						<AppTrunk />
					</BrowserRouter>
				</SnackbarProvider>
			</ThemeProvider>
		</Provider>
	);
}

export default AppRoot;
