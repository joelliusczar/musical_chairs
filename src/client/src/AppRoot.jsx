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
import { BrowserRouter } from "react-router-dom";
import { Provider } from "react-redux";
import store from "./reducers";
import { theme, drawerWidth } from "./style_config";
import { LoginModal } from "./Components/Accounts/AccountsLoginModal";
import { SnackbarProvider } from "notistack";
import { UserMenu } from "./Components/Accounts/UserMenu";
import {
	AuthContextProvider,
	useCurrentUser,
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
	const [loginOpen, setLoginOpen ] = useState(false);
	const [menuAnchor, setMenuAnchor ] = useState(null);
	const currentUser = useCurrentUser();

	const openUserMenu = (e) => {
		setMenuAnchor(e.currentTarget);
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
			<LoginModal open={loginOpen} setOpen={setLoginOpen} />
		</Box>
	);
}

function AppRoot() {
	const notistackRef = createRef();

	return (
		<Provider store={store}>
			<SnackbarProvider
				ref={notistackRef}
				onClick={() => notistackRef.current.closeSnackbar()}
			>
				<AuthContextProvider>
					<ThemeProvider theme={theme}>
						<BrowserRouter basename="/">
							<AppContextProvider>
								<AppTrunk />
							</AppContextProvider>
						</BrowserRouter>
					</ThemeProvider>
				</AuthContextProvider>
			</SnackbarProvider>
		</Provider>
	);
}

export default AppRoot;
