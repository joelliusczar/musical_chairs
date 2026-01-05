import React, { useEffect, useState } from "react";
import {
	Box,
} from "@mui/material";
import {
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import Loader from "../Shared/Loader";
import {
	Calls,
} from "../../API_Calls/songInfoCalls";
import { formatError } from "../../Helpers/error_formatter";
import { UserRoleDef, UserRoleDomain } from "../../constants";
import { useSnackbar } from "notistack";
import { UserRoleAssignmentTable } from "../Users/UserRoleAssignmentTable";
import { keyedSortFn } from "../../Helpers/array_helpers";
import {
	PageableListDataShape,
} from "../../Types/reducerTypes";
import {
	User,
	ActionRule,
	ActionRuleCreationInfo,
} from "../../Types/user_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import { useLocation } from "react-router-dom";
import { urlSafeBase64ToUnicode } from "../../Helpers/string_helpers";


const pathRoles = Object.keys(UserRoleDef)
	.map(k => UserRoleDef[k]).filter(v => v.startsWith(UserRoleDomain.PATH))
	.map(v => ({
		id: v,
		name: v,
	}));
pathRoles.unshift({
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

export const PathUserRoleAssignmentTable = () => {

	const [state, dispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<User>>(
			{ items: [], totalrows: 0}
		));
	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const { enqueueSnackbar } = useSnackbar();
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const nodeId = queryObj.get("nodeid") || "";
	const prefix = urlSafeBase64ToUnicode(nodeId);

	const { callStatus } = state;


	const addUser = async (user: User| null) => {
		if (!user) {
			console.error("provided user was null");
			return;
		}
		const rule = {
			name: UserRoleDef.PATH_VIEW,
			span: 0,
			count: 0,
			priority: null,
		};
		const requestObj = Calls.addPathUserRule({
			rule,
			nodeId,
			subjectuserkey: user.id,
		});
		try {
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

	useEffect(() => {
		document.title =
			`Musical Chairs - Users for ${prefix}`;
	},[prefix]);

	useEffect(() => {
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = new URLSearchParams(location.search);
		const prefix = queryObj.get("nodeid");
		if (prefix === null) return;

		const page = parseInt(queryObj.get("page") || "1");
		const limit = parseInt(queryObj.get("rows") || "50");
		const requestObj = Calls.getPathUsers({
			page: page - 1, limit: limit, prefix: prefix,
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
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	const addRole = async (rule: ActionRuleCreationInfo, user: User) => {
		try {
			const requestObj = Calls.addPathUserRule({
				rule,
				nodeId,
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
		try {
			const requestObj = Calls.removePathUserRule({
				rulename: role.name,
				nodeId,
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
		try {
			const requestObj = Calls.removePathUserRule({
				nodeId,
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

	return (
		<>
			<h1>
				Users for path: {prefix}
			</h1>
			<Box m={1}>
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
					availableRoles={pathRoles}
				/>
			</Loader>
		</>
	);
};

export default PathUserRoleAssignmentTable;
