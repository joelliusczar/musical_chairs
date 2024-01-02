import React, { useEffect, useState, useCallback } from "react";
import {
	Box,
} from "@mui/material";
import {
	dispatches,
} from "../../Reducers/waitingReducer";
import { useDataWaitingReducer } from "../../Reducers/dataWaitingReducer";
import Loader from "../Shared/Loader";
import {
	fetchStationUsers,
	addStationUserRule,
	removeStationUserRule,
} from "../../API_Calls/stationCalls";
import { useParams, useLocation } from "react-router-dom";
import { formatError } from "../../Helpers/error_formatter";
import { StationRouteSelect } from "./StationRouteSelect";
import { UrlBuilder } from "../../Helpers/pageable_helpers";
import { DomRoutes, UserRoleDef, UserRoleDomain } from "../../constants";
import { useSnackbar } from "notistack";
import { UserRoleAssignmentTable } from "../Users/UserRoleAssignmentTable";
import { keyedSortFn } from "../../Helpers/array_helpers";
import {
	PageableListStoreShape,
	WaitingTypes,
	PageableListDataShape,
	DataOrUpdater,
} from "../../Reducers/types/reducerTypes";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	User,
	ActionRule,
	ActionRuleCreationInfo,
} from "../../Types/user_types";
import { StationInfo } from "../../Types/station_types";


const stationRoles = Object.keys(UserRoleDef)
	.map(k => UserRoleDef[k]).filter(v => v.startsWith(UserRoleDomain.STATION))
	.map(v => ({
		id: v,
		name: v,
	}));
stationRoles.unshift({
	id: "",
	name: "",
});


const ruleUpdatePaths = {
	[WaitingTypes.add]: (state: PageableListStoreShape<User>, payload: User) => {
		const items = [...state.data.items, payload]
			.sort(keyedSortFn("username"));
		return {
			...state,
			data: {
				...state.data,
				items: items,
			},
		};
	},
	[WaitingTypes.remove]: (
		state: PageableListStoreShape<User>,
		payload: { key: number | string}
	) => {
		const { key } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === parseInt(key as string));
		items.splice(idx, 1);
		return {
			...state,
			data: {
				...state.data,
				items: items,
			},
		};
	},
	[WaitingTypes.updateItem]: (
		state: PageableListStoreShape<User>,
		payload: {
			key: string | number,
			dataOrUpdater: DataOrUpdater<User>
		}
	) => {
		const { key, dataOrUpdater } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === parseInt(key as string));
		if (idx > -1) {
			if (typeof dataOrUpdater === "function") {
				items.splice(idx, 1, dataOrUpdater(items[idx]));
			}
			else {
				items.splice(idx, 1, dataOrUpdater);
			}
			const sortedItems = items.sort(keyedSortFn("username"));
			return {
				...state,
				data: {
					...state.data,
					items: sortedItems,
				},
			};
		}
		else {
			console.error("Item was not found in local store.");
			return state;
		}
	},
};

export const StationUserRoleAssignmentTable = () => {

	const [state, dispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<User>>(
			{ items: [], totalrows: 0 }
		),
		{reducerMods: ruleUpdatePaths}
	);
	const [selectedStation, setSelectedStation] = useState<StationInfo | null>();
	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const pathVars = useParams();
	const location = useLocation();
	const { enqueueSnackbar } = useSnackbar();

	const { callStatus } = state;

	const urlBuilder = new UrlBuilder(DomRoutes.stationUsers);

	const addUser = async (user: User | null) => {
		if (!user) {
			enqueueSnackbar("provided user was null", { variant: "error"});
			return;
		}
		if (!pathVars.stationkey || !pathVars.ownerkey) {
			enqueueSnackbar("user or station is missing", { variant: "error"});
			return;
		}
		try {
			const rule = {
				name: UserRoleDef.STATION_VIEW,
				span: 0,
				count: 0,
				priority: null,
			};
			const addedRule = await addStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				rule,
				subjectuserkey: user.id,
			});
			dispatch(dispatches.add({
				...user,
				roles: [...user.roles, addedRule],
			}));
			enqueueSnackbar("User added!", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	const setStationCallback = useCallback(
		(s: StationInfo | null) => setSelectedStation(s),
		[setSelectedStation]
	);

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayname || ""}`;
		document.title =
			`Musical Chairs - Users for ${stationTitle}`;
	},[selectedStation]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			if (!pathVars.stationkey || !pathVars.ownerkey) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			dispatch(dispatches.started());
			try {
				const data = await fetchStationUsers({
					stationkey: pathVars.stationkey,
					ownerkey: pathVars.ownerkey,
					page: page - 1,
					limit: limit,
				});
				dispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);

			}
			catch (err) {
				dispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
	},[
		dispatch,
		pathVars.stationkey,
		pathVars.ownerkey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	const addRole = async (rule: ActionRuleCreationInfo, user: User) => {
		if (!pathVars.stationkey || !pathVars.ownerkey) {
			console.error("user or station is missing");
			return;
		}
		try {
			const addedRule = await addStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				rule,
				subjectuserkey: user.id,
			});
			dispatch(dispatches.update(
				user.id,
				{...user,
					roles: [...user.roles, addedRule].sort(keyedSortFn("name")),
				}
			));
			enqueueSnackbar("Role added!", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	const removeRole = async (role: ActionRule, user: User) => {
		if (!pathVars.stationkey || !pathVars.ownerkey) {
			console.error("user or station is missing");
			return;
		}
		try {
			await removeStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				rulename: role.name,
				subjectuserkey: user.id,
			});
			const roles = [...user.roles];
			const idx = roles.findIndex(r => r.name === role.name);
			if (idx > -1 ) {
				roles.splice(idx, 1);
				dispatch(dispatches.update(
					user.id,
					{...user,
						roles: roles,
					}
				));
			}
			else {
				enqueueSnackbar("Local role not found?", { variant: "error"});
			}
			enqueueSnackbar(`${role.name} removed!`, { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	const removeUser = async (user: User) => {
		if (!pathVars.stationkey || !pathVars.ownerkey) {
			console.error("user or station is missing");
			return;
		}
		try {
			await removeStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				subjectuserkey: user.id,
			});
			dispatch(dispatches.remove(user.id));
			enqueueSnackbar(`${user.username} removed!`, { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	const stationName =
		selectedStation?.displayname || selectedStation?.name || "";
	return (
		<>
			<h1>
				Users for station: {stationName}
			</h1>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={urlBuilder.getOtherUrl}
					onChange={setStationCallback}
					unrendered
				/>
			</Box>
			<Loader
				status={callStatus}
				error={state.error}
			>
				<UserRoleAssignmentTable
					onUserSelect={addUser}
					users={state.data?.items || []}
					removeRole={removeRole}
					removeUser={removeUser}
					addRole={addRole}
					availableRoles={stationRoles}
				/>
			</Loader>
		</>
	);
};

StationUserRoleAssignmentTable.propTypes = {
};