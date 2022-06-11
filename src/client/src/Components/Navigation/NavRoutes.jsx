import React from "react";
import { Route, Switch, NavLink, useHistory } from "react-router-dom";
import { List, ListItem } from "@mui/material";
import Queue from "../Queue/Queue";
import History from "../History/History";
import Stations from "../Stations/Stations";
import SongCatalogue from "../Song_Catalogue/SongCatalogue";
import { AccountEdit } from "../Accounts/AccountsEdit";
import { LoginForm } from "../Accounts/AccountsLoginForm";
import { currentUserSelector } from "../Accounts/accounts_slice";
import { NotFound, GoToNotFound } from "../Shared/NotFound";
import { DomRoutes } from "../../constants";
import { useSelector } from "react-redux";


export function NavMenu() {
	return (
		<List>
			<ListItem button component={NavLink} to="/home">
				Home
			</ListItem>
			<ListItem button component={NavLink} to={DomRoutes.queue} >
				Queue
			</ListItem>
			<ListItem button component={NavLink} to={DomRoutes.history}>
				History
			</ListItem>
			<ListItem button component={NavLink} to={DomRoutes.stations}>
				Stations
			</ListItem>
			<ListItem button component={NavLink} to={DomRoutes.songCatalogue}>
				Song Catalogue
			</ListItem>
		</List>
	);
}

export function AppRoutes() {

	const urlHistory = useHistory();
	const currentUser = useSelector(currentUserSelector);

	return (
		<Switch>
			<Route path={`${DomRoutes.queue}:station?`}>
				<Queue />
			</Route>
			<Route path={`${DomRoutes.history}:station?`}>
				<History />
			</Route>
			<Route path={DomRoutes.stations}>
				<Stations />
			</Route>
			<Route path={`${DomRoutes.songCatalogue}:station?`}>
				<SongCatalogue />
			</Route>
			<Route path={`${DomRoutes.accountsEdit}:id?`}>
				<AccountEdit />
			</Route>
			{!currentUser.username && <Route path={`${DomRoutes.accountsLogin}`} >
				<LoginForm
					afterSubmit={() => urlHistory.push("")}
				/>
			</Route>}
			<Route path={`${DomRoutes.notFound}`}>
				<NotFound />
			</Route>
			<GoToNotFound />
		</Switch>
	);
}
