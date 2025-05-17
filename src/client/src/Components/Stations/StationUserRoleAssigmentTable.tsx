import React, { useEffect, useState, useCallback } from "react";
import {
	Box,
} from "@mui/material";
import { 
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
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
	PageableListDataShape,
} from "../../Types/reducerTypes";
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


const replaceUserInState = (
	state: RequiredDataStore<PageableListDataShape<User>>,
	userCopy: User
) => {
	const items = [...state.data.items];
	const idx = items.findIndex(i => i.id === userCopy.id);
	if (idx > -1) {
		items[idx] = userCopy;
		return {
			...state,
			data: {
				...state.data,
				items: items,
			},
		};
	}
	console.error("Item was not found in local store.");
	return state;
};

export const StationUserRoleAssignmentTable = () => {

	const [state, dispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<User>>(
			{ items: [], totalrows: 0 }
		)
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
			const requestObj = addStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				rule,
				subjectuserkey: user.id,
			});
			const addedRule = await requestObj.call();
			dispatch(dispatches.update((state) => {
				const userCopy = {
					...user,
					roles: [...user.roles, addedRule],
				};
				const items = [...state.data.items, userCopy]
					.sort(keyedSortFn("username"));
				return {
					...state,
					data: {
						...state.data,
						items: items,
					},
				};
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
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = new URLSearchParams(location.search);
		if (!pathVars.stationkey || !pathVars.ownerkey) return;

		const page = parseInt(queryObj.get("page") || "1");
		const limit = parseInt(queryObj.get("rows") || "50");
		const requestObj = fetchStationUsers({
			stationkey: pathVars.stationkey,
			ownerkey: pathVars.ownerkey,
			page: page - 1,
			limit: limit,
		});
		const fetch = async () => {
			dispatch(dispatches.started());
			try {
				const data = await requestObj.call();
				dispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);

			}
			catch (err) {
				dispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
		return () => requestObj.abortController.abort();
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
			const requestObj = addStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				rule,
				subjectuserkey: user.id,
			});
			const addedRule = await requestObj.call();
			dispatch(dispatches.update((state) => {
				const userCopy = {
					...user,
					roles: [...user.roles, addedRule].sort(keyedSortFn("name")),
				};
				return replaceUserInState(state, userCopy);
			}));
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
			const requestObj = removeStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				rulename: role.name,
				subjectuserkey: user.id,
			});
			await requestObj.call();
			dispatch(dispatches.update((state) => {
				const roles = [...user.roles];
				const ridx = roles.findIndex(r => r.name === role.name);
				if (ridx > -1 ) {
					roles.splice(ridx, 1);
					const userCopy = {
						...user,
						roles: roles,
					};
					return replaceUserInState(state, userCopy);
				}
				console.error("Item was not found in local store.");
				return state;
			}));
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
			const requestObj = removeStationUserRule({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				subjectuserkey: user.id,
			});
			await requestObj.call();
			dispatch(dispatches.update((state) => {
				const items = [...state.data.items];
				const idx = items.findIndex(i => i.id === user.id);
				if (idx > -1 ) {
					items.splice(idx, 1);
					return {
						...state,
						data: {
							...state.data,
							items: items,
						},
					};
				}
				console.error("Item was not found in local store.");
				return state;
			}));
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

export default StationUserRoleAssignmentTable;