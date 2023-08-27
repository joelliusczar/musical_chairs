import React, { useEffect } from "react";
import { Route, Routes, NavLink, useNavigate } from "react-router-dom";
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

	const navigate = useNavigate();
	const currentUser = useCurrentUser();

	useEffect(() => {
		if (!currentUser.username) {
			const cookieObj = cookieToObject(document.cookie);
			if (!cookieObj["username"]) {
				navigate("/");
			}
		}
	},[navigate, currentUser]);

	return (
		<Routes>
			<Route
				path={`${DomRoutes.queue({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
				element={<Queue />}
			/>
			<Route
				path={`${DomRoutes.history({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
				element={<History />}
			/>
			<Route
				path={`${DomRoutes.stations({
					ownerKey: ":ownerKey?",
				})}`}
				element={<Stations />}
			/>
			<Route
				path={`${DomRoutes.songCatalogue({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
				element={<SongCatalogue />}
			/>
			{currentUser.username && <Route
				path={DomRoutes.stationUsers({
					stationKey: ":stationKey",
					ownerKey: ":ownerKey",
				})}
				element={<StationUserRoleAssignmentTable />}
			/>}
			{currentUser.username && <Route
				path={DomRoutes.pathUsers()}
				element={<PathUserRoleAssignmentTable />}
			/>}
			{!currentUser.username &&<Route
				path={DomRoutes.accountsNew()}
				element={<AccountsNew />}
			/>}
			{!currentUser.username && <Route
				path={DomRoutes.accountsLogin()}
				element={<LoginForm
					afterSubmit={() => navigate("")}
				/>}
			/>}
			{currentUser.username &&
			<Route
				path={DomRoutes.accountsEdit({
					subjectUserKey: ":subjectUserKey",
				})}
			>
				<AccountsEdit />
			</Route>}
			<Route
				path={DomRoutes.accountsList()}
				element={
					<PrivateRoute
						scopes={[UserRoleDef.USER_LIST, UserRoleDef.USER_EDIT]}
						element={<AccountsList />}
					/>
				}
			/>
			<Route
				path={DomRoutes.accountsRoles({ subjectUserKey: ":subjectUserKey"})}
				element={
					<PrivateRoute
						element={<SiteUserRoleAssignmentTable />}
						scopes={[UserRoleDef.ADMIN, UserRoleDef.SITE_USER_ASSIGN]}
					/>
				}
			/>
			<Route
				path={`${DomRoutes.stationsEdit({
					stationKey: ":stationKey?",
					ownerKey: ":ownerKey",
				})}`}
				element={<StationEdit />}
			/>
			<Route
				path={`${DomRoutes.stationsAdd()}`}
				element={
					<PrivateRoute
						element={<StationEdit />}
						scopes={[UserRoleDef.STATION_CREATE]}
					/>
				}
			/>
			<Route
				path={`${DomRoutes.songEdit()}`}
				element={<SongEdit />}
			/>
			<Route
				path={DomRoutes.songTree()}
				element={
					<PrivateRoute
						element={<SongTree />}
						scopes={[
							UserRoleDef.PATH_LIST,
							UserRoleDef.PATH_EDIT,
							UserRoleDef.SONG_DOWNLOAD,
						]}
					/>
				}
			/>
			<Route
				path="/"
				element={<Stations />}
			/>
			<Route path="*" element={<NotFound />} />
		</Routes>
	);
}