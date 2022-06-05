import React from "react";
import { Route, Switch, NavLink, Redirect } from "react-router-dom";
import { List, ListItem } from "@mui/material";
import Queue from "../Queue/Queue";
import History from "../History/History";
import Stations from "../Stations/Stations";
import SongCatalogue from "../Song_Catalogue/SongCatalogue";
import { AccountEdit } from "../Accounts/AccountsEdit";
import { NotFound } from "../Shared/NotFound";
import { DomRoutes } from "../../constants";


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
			<Route path={`${DomRoutes.notFound}`}>
				<NotFound />
			</Route>
			<Redirect to={`${DomRoutes.notFound}`} />
		</Switch>
	);
}
