import React, { useEffect } from "react";
import { Route, Switch, NavLink, useHistory } from "react-router-dom";
import { List, ListItem } from "@mui/material";
import { Queue } from "../Queue/Queue";
import { History } from "../History/History";
import { Stations } from "../Stations/Stations";
import { SongCatalogue } from "../Song_Catalogue/SongCatalogue";
import { AccountsNew } from "../Accounts/AccountsNew";
import { AccountsEdit } from "../Accounts/AccountsEdit";
import { LoginForm } from "../Accounts/AccountsLoginForm";
import { AccountsList } from "../Accounts/AccountsList";
import { StationEdit } from "../Stations/StationEdit";
import { SongTree } from "../Songs/SongTree";
import { SongEdit } from "../Songs/SongEdit";
import { NotFound } from "../Shared/RoutingErrors";
import { DomRoutes, UserRoleDef } from "../../constants";
import { PrivateRoute } from "../Shared/PrivateRoute";
import {
	useCurrentUser,
	useHasAnyRoles,
} from "../../Context_Providers/AuthContext";
import { cookieToObject } from "../../Helpers/browser_helpers";
import {
	StationUserRoleAssignmentTable,
} from "../Stations/StationUserRoleAssigmentTable";
import {
	PathUserRoleAssignmentTable,
} from "../Songs/PathUserRoleAssigmentTable";
import {
	SiteUserRoleAssignmentTable,
} from "../Users/SiteUserRoleAssignmentTable";


export function NavMenu() {

	const currentUser = useCurrentUser();

	const canOpenAccountList = useHasAnyRoles([
		UserRoleDef.USER_EDIT,
		UserRoleDef.USER_LIST,
	]);

	return (
		<List>
			{currentUser.username && <ListItem
				component={NavLink}
				to={DomRoutes.queue({
					ownerKey: currentUser.username,
				})}
			>
				Queue
			</ListItem>}
			{currentUser.username && <ListItem
				component={NavLink}
				to={DomRoutes.history({
					ownerKey: currentUser.username,
				})}
			>
				History
			</ListItem>}
			{currentUser.username && <ListItem
				component={NavLink}
				to={DomRoutes.stations({
					ownerKey: currentUser.username,
				})}>
				Stations
			</ListItem>}
			<ListItem
				component={NavLink}
				to={DomRoutes.stations()}>
				All Stations
			</ListItem>
			<ListItem
				component={NavLink}
				to={DomRoutes.songTree()}>
				Song Directory
			</ListItem>
			{canOpenAccountList &&
			<ListItem component={NavLink} to={DomRoutes.accountsList()}>
				Accounts List
			</ListItem>}
		</List>
	);
}

export function AppRoutes() {

	const urlHistory = useHistory();
	const currentUser = useCurrentUser();

	useEffect(() => {
		if (!currentUser.username) {
			const cookieObj = cookieToObject(document.cookie);
			if (!cookieObj["username"]) {
				urlHistory.push("/");
			}
		}
	},[urlHistory, currentUser]);

	return (
		<Switch>
			<Route
				path={`${DomRoutes.queue({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
			>
				<Queue />
			</Route>
			<Route
				path={`${DomRoutes.history({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
			>
				<History />
			</Route>
			<Route
				path={`${DomRoutes.stations({
					ownerKey: ":ownerKey?",
				})}`}
			>
				<Stations />
			</Route>
			<Route
				path={`${DomRoutes.songCatalogue({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
			>
				<SongCatalogue />
			</Route>
			{currentUser.username && <Route
				path={DomRoutes.stationUsers({
					stationKey: ":stationKey",
					ownerKey: ":ownerKey",
				})}
			>
				<StationUserRoleAssignmentTable />
			</Route>}
			{currentUser.username && <Route
				path={DomRoutes.pathUsers()}
			>
				<PathUserRoleAssignmentTable />
			</Route>}
			{!currentUser.username &&<Route path={DomRoutes.accountsNew()}>
				<AccountsNew />
			</Route>}
			{!currentUser.username && <Route path={DomRoutes.accountsLogin()} >
				<LoginForm
					afterSubmit={() => urlHistory.push("")}
				/>
			</Route>}
			{currentUser.username &&
			<Route
				path={DomRoutes.accountsEdit({
					subjectUserKey: ":subjectUserKey",
				})}
			>
				<AccountsEdit />
			</Route>}
			<PrivateRoute
				scopes={[UserRoleDef.USER_LIST, UserRoleDef.USER_EDIT]}
				path={DomRoutes.accountsList()}
			>
				<AccountsList />
			</PrivateRoute>
			<PrivateRoute
				path={DomRoutes.accountsRoles({ subjectUserKey: ":subjectUserKey"})}
				scopes={[UserRoleDef.ADMIN, UserRoleDef.SITE_USER_ASSIGN]}
			>
				<SiteUserRoleAssignmentTable />
			</PrivateRoute>
			<Route
				path={`${DomRoutes.stationsEdit({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
			>
				<StationEdit />
			</Route>
			<PrivateRoute
				path={`${DomRoutes.stationsAdd()}`}
				scopes={[UserRoleDef.STATION_CREATE]}
			>
				<StationEdit />
			</PrivateRoute>
			<Route
				path={`${DomRoutes.songEdit()}`}
			>
				<SongEdit />
			</Route>
			<PrivateRoute
				path={DomRoutes.songTree()}
				scopes={[
					UserRoleDef.PATH_LIST,
					UserRoleDef.PATH_EDIT,
					UserRoleDef.SONG_DOWNLOAD,
				]}
			>
				<SongTree />
			</PrivateRoute>
			<Route exact path="/">
				<Stations />
			</Route>
			<Route>
				<NotFound />
			</Route>
		</Switch>
	);
}
