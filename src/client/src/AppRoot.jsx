import React from "react";
import "./App.css";
import { AppBar, Drawer, ThemeProvider, Typography } from "@mui/material";
import { makeStyles } from "@mui/styles";
import { AppRoutes, NavMenu } from "./Components/Navigation/NavRoutes";
import { BrowserRouter } from "react-router-dom";
import { apiAddress } from "./constants";
import { Provider } from "react-redux";
import store from "./reducers";
import { theme, drawerWidth } from "./style_config";

export const useStyles = makeStyles((theme) => ({
	root: {
		display: "flex",
	},
	appBar: {
		marginLeft: drawerWidth,
		width: `calc(100% - ${drawerWidth}px)`,
	},
	content: {
		flexGrow: 1,
		padding: theme.spacing(3),
	},
	drawer: {
		flexShrink: 0,
		width: drawerWidth,
	},
	drawerPaper: {
		width: drawerWidth,
	},
	toolbar: theme.mixins.toolbar,
}));

function AppTrunk() {
	const classes = useStyles();
	
	return (
		<div className={classes.root}>
			<AppBar 
				color="primary" 
				position="fixed" 
				className={classes.appBar}
			>
				<Typography variant="h1">Musical Chairs</Typography>
			</AppBar>
			<Drawer
				variant="permanent"
				anchor="left"
				className={classes.drawer}
				classes={{
					paper: classes.drawerPaper,
				}}
			>
				<NavMenu />
			</Drawer>
			<main className={classes.content}>
				<div className={classes.toolbar} />
				<Typography variant="h1">{apiAddress}</Typography>
				<AppRoutes />
			</main>
		</div>
	);
}

function AppRoot() {
	
	return (
		<Provider store={store}>
			<ThemeProvider theme={theme}>
				{<BrowserRouter basename="/">
					<AppTrunk />
				</BrowserRouter>}
			</ThemeProvider>
		</Provider>
	);
}

export default AppRoot;
