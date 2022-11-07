import React from "react";
import { Route, Switch, NavLink, useHistory } from "react-router-dom";
import { List, ListItem } from "@mui/material";
import Queue from "../Queue/Queue";
import History from "../History/History";
import Stations from "../Stations/Stations";
import SongCatalogue from "../Song_Catalogue/SongCatalogue";
import { AccountsNew } from "../Accounts/AccountsNew";
import { LoginForm } from "../Accounts/AccountsLoginForm";
import { AccountsList } from "../Accounts/AccountsList";
import { AccountsRoles } from "../Accounts/AccountsRoles";
import { StationEdit } from "../Stations/StationEdit";
import { SongTree } from "../Songs/SongTree";
import { SongEdit } from "../Songs/SongEdit";
import { NotFound } from "../Shared/RoutingErrors";
import { DomRoutes, UserRoleDef } from "../../constants";
import { PrivateRoute } from "../Shared/PrivateRoute";
import { useCurrentUser } from "../../Context_Providers/AuthContext";



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
			<ListItem button component={NavLink} to={DomRoutes.songTree}>
				Song Directory
			</ListItem>
			<ListItem button component={NavLink} to={DomRoutes.accountsList}>
				Accounts List
			</ListItem>
		</List>
	);
}

export function AppRoutes() {

	const urlHistory = useHistory();
	const currentUser = useCurrentUser();

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
			{!currentUser.username &&<Route path={DomRoutes.accountsNew}>
				<AccountsNew />
			</Route>}
			{!currentUser.username && <Route path={DomRoutes.accountsLogin} >
				<LoginForm
					afterSubmit={() => urlHistory.push("")}
				/>
			</Route>}
			<Route path={DomRoutes.accountsList}>
				<AccountsList />
			</Route>
			<PrivateRoute
				path={`${DomRoutes.accountsRoles}:id`}
				scopes={[UserRoleDef.ADMIN]}
			>
				<AccountsRoles />
			</PrivateRoute>
			<PrivateRoute
				path={`${DomRoutes.stationsEdit}`}
				scopes={[UserRoleDef.STATION_EDIT]}
			>
				<StationEdit />
			</PrivateRoute>
			<PrivateRoute
				path={`${DomRoutes.songEdit}`}
				scopes={[UserRoleDef.SONG_EDIT]}
			>
				<SongEdit />
			</PrivateRoute>
			<PrivateRoute
				path={DomRoutes.songTree}
				scopes={[
					UserRoleDef.SONG_TREE_LIST,
					UserRoleDef.SONG_EDIT,
					UserRoleDef.SONG_DOWNLOAD,
				]}
			>
				<SongTree />
			</PrivateRoute>
			<Route>
				<NotFound />
			</Route>
		</Switch>
	);
}
