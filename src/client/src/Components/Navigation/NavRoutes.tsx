import React from "react";
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
} from "../../Context_Providers/AuthContext/AuthContext";
import {
	StationUserRoleAssignmentTable,
} from "../Stations/StationUserRoleAssigmentTable";
import {
	PathUserRoleAssignmentTable,
} from "../Songs/PathUserRoleAssigmentTable";
import {
	SiteUserRoleAssignmentTable,
} from "../Users/SiteUserRoleAssignmentTable";
import { AlbumTableView } from "../Albums/AlbumTableView";
import { AlbumEditScreen } from "../Albums/AlbumEditScreen";
import { ArtistTableView } from "../Artists/ArtistTableView";
import { ArtistEditScreen } from "../Artists/ArtistEditScreen";


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
					ownerkey: currentUser.username,
				})}
			>
				Queue
			</ListItem>}
			{currentUser.username && <ListItem
				component={NavLink}
				to={DomRoutes.history({
					ownerkey: currentUser.username,
				})}
			>
				History
			</ListItem>}
			{currentUser.username && <ListItem
				component={NavLink}
				to={DomRoutes.stations({
					ownerkey: currentUser.username,
				})}>
				My Stations
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
			<ListItem 
				component={NavLink}
				to={DomRoutes.albumPage()}
			>
				Albums
			</ListItem>
			<ListItem 
				component={NavLink}
				to={DomRoutes.artistPage()}
			>
				Artists
			</ListItem>
			{canOpenAccountList &&
			<ListItem component={NavLink} to={DomRoutes.accountsList()}>
				Accounts List
			</ListItem>}
		</List>
	);
}

export function AppRoutes() {


	const currentUser = useCurrentUser();


	const navigate = useNavigate();


	return (
		<Routes>
			<Route 
				path={DomRoutes.artistPage()}
				element={<ArtistTableView />}
			/>
			<Route 
				path={DomRoutes.artist({
					id: ":id",
				})}
				element={<ArtistEditScreen />}
			/>
			<Route 
				path={DomRoutes.albumPage()}
				element={<AlbumTableView />}
			/>
			<Route 
				path={DomRoutes.album({
					id: ":id",
				})}
				element={<AlbumEditScreen />}
			/>
			<Route
				path={`${DomRoutes.queue({ 
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
				})}`}
				element={<Queue />}
			/>
			<Route
				path={`${DomRoutes.queue({
					ownerkey: ":ownerkey",
				})}`}
				element={<Queue />}
			/>
			<Route
				path={`${DomRoutes.history({
					stationkey: ":stationkey?",
					ownerkey: ":ownerkey",
				})}`}
				element={<History />}
			/>
			<Route
				path={`${DomRoutes.stations()}`}
				element={<Stations />}
			/>
			<Route
				path={`${DomRoutes.stations({
					ownerkey: ":ownerkey",
				})}`}
				element={<Stations />}
			/>
			<Route
				path={`${DomRoutes.songCatalogue({
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
				})}`}
				element={<SongCatalogue />}
			/>
			<Route
				path={`${DomRoutes.songCatalogue({
					ownerkey: ":ownerkey",
				})}`}
				element={<SongCatalogue />}
			/>
			{currentUser.username && <Route
				path={DomRoutes.stationUsers({
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
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
					subjectuserkey: ":subjectuserkey",
				})}
				element={<AccountsEdit />}
			/>}
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
				path={DomRoutes.accountsRoles({ subjectuserkey: ":subjectuserkey"})}
				element={
					<PrivateRoute
						element={<SiteUserRoleAssignmentTable />}
						scopes={[UserRoleDef.ADMIN, UserRoleDef.SITE_USER_ASSIGN]}
					/>
				}
			/>
			<Route
				path={`${DomRoutes.stationsEdit({
					ownerkey: ":ownerkey",
				})}`}
				element={<StationEdit />}
			/>
			<Route
				path={`${DomRoutes.stationsEdit({
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
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
					<SongTree />
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