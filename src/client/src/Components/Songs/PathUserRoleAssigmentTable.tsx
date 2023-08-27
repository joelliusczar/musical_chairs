import React, { useEffect, useState } from "react";
import {
	Box,
} from "@mui/material";
import {
	dispatches,
	globalStoreLogger,
} from "../../Reducers/waitingReducer";
import {
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import Loader from "../Shared/Loader";
import {
	fetchPathUsers,
	addPathUserRule,
	removePathUserRule,
} from "../../API_Calls/songInfoCalls";
import { formatError } from "../../Helpers/error_formatter";
import { UserRoleDef, UserRoleDomain } from "../../constants";
import { useSnackbar } from "notistack";
import { UserRoleAssignmentTable } from "../Users/UserRoleAssignmentTable";
import { keyedSortFn } from "../../Helpers/array_helpers";
import { KeyType } from "../../Types/generic_types";
import {
	PageableListDataShape,
	PageableListStoreShape,
	WaitingTypes,
	DataOrUpdater,
} from "../../Reducers/types/reducerTypes";
import {
	User,
	ActionRule,
	ActionRuleCreationInfo,
} from "../../Types/user_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";


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
		payload: { key: KeyType}
	) => {
		const { key } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === (+key * 1));
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
			key: KeyType,
			dataOrUpdater: DataOrUpdater<User>
		}
	) => {
		const { key, dataOrUpdater } = payload;
		const items = [...state.data.items];
		const idx = items.findIndex(x => x.id === (+key * 1));
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

export const PathUserRoleAssignmentTable = () => {

	const [state, dispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<User>>(
			{ items: [], totalRows: 0}
		),
		{
			reducerMods: ruleUpdatePaths,
			middleware:[globalStoreLogger("path users")],
		}
	);
	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const { enqueueSnackbar } = useSnackbar();
	const queryObj = new URLSearchParams(location.search);
	const prefix = queryObj.get("prefix");

	const { callStatus } = state;


	const addUser = async (user: User| null) => {
		if (!user) {
			console.error("provided user was null");
			return;
		}
		try {
			const rule = {
				name: UserRoleDef.PATH_VIEW,
				span: 0,
				count: 0,
				priority: null,
			};
			const addedRule = await addPathUserRule({
				rule,
				prefix,
				subjectUserKey: user.id,
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

	useEffect(() => {
		document.title =
			`Musical Chairs - Users for ${prefix}`;
	},[prefix]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			const prefix = queryObj.get("prefix");
			if (prefix === null) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			dispatch(dispatches.started());
			try {
				const data = await fetchPathUsers({
					page: page - 1, limit: limit, prefix: prefix,
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
		fetchPathUsers,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	const addRole = async (rule: ActionRuleCreationInfo, user: User) => {
		try {
			const addedRule = await addPathUserRule({
				rule,
				prefix,
				subjectUserKey: user.id,
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
		try {
			await removePathUserRule({
				ruleName: role.name,
				prefix,
				subjectUserKey: user.id,
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
		try {
			await removePathUserRule({
				prefix,
				subjectUserKey: user.id,
			});
			dispatch(dispatches.remove(user.id));
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

PathUserRoleAssignmentTable.propTypes = {
};

