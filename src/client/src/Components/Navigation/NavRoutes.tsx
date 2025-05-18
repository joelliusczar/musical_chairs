import React, { lazy, Suspense } from "react";
import { Route, Routes, NavLink, useNavigate } from "react-router-dom";
import { List, ListItem } from "@mui/material";
const Queue = lazy(() => import("../Queue/Queue"));
const History = lazy(() => import("../History/History"));
const Stations = lazy(() => import("../Stations/Stations"));
const SongCatalogue = lazy(() => import("../Song_Catalogue/SongCatalogue"));
const AccountsNew = lazy(() => import("../Accounts/AccountsNew"));
const AccountsEdit = lazy(() => import("../Accounts/AccountsEdit"));
const LoginForm = lazy(() => import("../Accounts/AccountsLoginForm"));
const AccountsList = lazy(() => import("../Accounts/AccountsList"));
const StationEdit = lazy(() => import("../Stations/StationEdit"));
const SongTree = lazy(() => import("../Songs/SongTree"));
const SongEdit = lazy(() => import("../Songs/SongEdit"));
import { NotFound } from "../Shared/RoutingErrors";
import { DomRoutes, UserRoleDef } from "../../constants";
import { PrivateRoute } from "../Shared/PrivateRoute";
import {
	useCurrentUser,
	useHasAnyRoles,
} from "../../Context_Providers/AuthContext/AuthContext";
const StationUserRoleAssignmentTable = 
	lazy(() => import("../Stations/StationUserRoleAssigmentTable"));
const PathUserRoleAssignmentTable =
	lazy(() => import("../Songs/PathUserRoleAssigmentTable"));
const SiteUserRoleAssignmentTable =
	lazy(() => import("../Users/SiteUserRoleAssignmentTable"));
const AlbumTableView = lazy(() => import("../Albums/AlbumTableView"));
const AlbumEditScreen = lazy(() => import("../Albums/AlbumEditScreen"));
const ArtistEditScreen = lazy(() => import("../Artists/ArtistEditScreen"));
const ArtistTableView = lazy(() => import("../Artists/ArtistTableView"));


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
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<ArtistTableView />
					</Suspense>
				}
			/>
			<Route 
				path={DomRoutes.artist({
					id: ":id",
				})}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<ArtistEditScreen />
					</Suspense>
				}
			/>
			<Route 
				path={DomRoutes.albumPage()}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<AlbumTableView />
					</Suspense>
				}
			/>
			<Route 
				path={DomRoutes.album({
					id: ":id",
				})}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<AlbumEditScreen />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.queue({ 
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<Queue />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.queue({
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<Queue />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.history({
					stationkey: ":stationkey?",
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<History />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.stations()}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<Stations />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.stations({
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<Stations />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.songCatalogue({
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<SongCatalogue />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.songCatalogue({
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<SongCatalogue />
					</Suspense>
				}
			/>
			{currentUser.username && <Route
				path={DomRoutes.stationUsers({
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
				})}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<StationUserRoleAssignmentTable />
					</Suspense>
				}
			/>}
			{currentUser.username && <Route
				path={DomRoutes.pathUsers()}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<PathUserRoleAssignmentTable />
					</Suspense>
				}
			/>}
			{!currentUser.username &&<Route
				path={DomRoutes.accountsNew()}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<AccountsNew />
					</Suspense>
				}
			/>}
			{!currentUser.username && <Route
				path={DomRoutes.accountsLogin()}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<LoginForm
							afterSubmit={() => navigate("")}
						/>
					</Suspense>
				}
			/>}
			{currentUser.username &&
			<Route
				path={DomRoutes.accountsEdit({
					subjectuserkey: ":subjectuserkey",
				})}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<AccountsEdit />
					</Suspense>
				}
			/>}
			<Route
				path={DomRoutes.accountsList()}
				element={
					<PrivateRoute
						scopes={[UserRoleDef.USER_LIST, UserRoleDef.USER_EDIT]}
						element={
							<Suspense fallback={<div>Loading...</div>}>
								<AccountsList />
							</Suspense>
						}
					/>
				}
			/>
			<Route
				path={DomRoutes.accountsRoles({ subjectuserkey: ":subjectuserkey"})}
				element={
					<PrivateRoute
						element={
							<Suspense fallback={<div>Loading...</div>}>
								<SiteUserRoleAssignmentTable />
							</Suspense>
						}
						scopes={[UserRoleDef.ADMIN, UserRoleDef.SITE_USER_ASSIGN]}
					/>
				}
			/>
			<Route
				path={`${DomRoutes.stationsEdit({
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<StationEdit />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.stationsEdit({
					stationkey: ":stationkey",
					ownerkey: ":ownerkey",
				})}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<StationEdit />
					</Suspense>
				}
			/>
			<Route
				path={`${DomRoutes.stationsAdd()}`}
				element={
					<PrivateRoute
						element={
							<Suspense fallback={<div>Loading...</div>}>
								<StationEdit />
							</Suspense>
						}
						scopes={[UserRoleDef.STATION_CREATE]}
					/>
				}
			/>
			<Route
				path={`${DomRoutes.songEdit()}`}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<SongEdit />
					</Suspense>
				}
			/>
			<Route
				path={DomRoutes.songTree()}
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<SongTree />
					</Suspense>
				}
			/>
			<Route
				path="/"
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<Stations />
					</Suspense>}
			/>
			<Route 
				path="*" 
				element={
					<Suspense fallback={<div>Loading...</div>}>
						<NotFound />
					</Suspense>
				} />
		</Routes>
	);
}