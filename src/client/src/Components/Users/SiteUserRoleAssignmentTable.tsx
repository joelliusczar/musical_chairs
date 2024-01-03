import React, { useEffect, useState } from "react";
import {
	Box,
} from "@mui/material";
import {
	dispatches,
	globalStoreLogger,
} from "../../Reducers/waitingReducer";
import { useDataWaitingReducer } from "../../Reducers/dataWaitingReducer";
import Loader from "../Shared/Loader";
import {
	addSiteUserRule,
	removeSiteUserRule,
	fetchUser,
} from "../../API_Calls/userCalls";
import { formatError } from "../../Helpers/error_formatter";
import { UserRoleDef } from "../../constants";
import { useSnackbar } from "notistack";
import { UserRoleAssignmentTable } from "./UserRoleAssignmentTable";
import { keyedSortFn } from "../../Helpers/array_helpers";
import { useParams, useLocation } from "react-router-dom";
import {
	WaitingTypes,
	SimpleStoreShape,
} from "../../Reducers/types/reducerTypes";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	User,
	ActionRuleCreationInfo,
	ActionRule,
} from "../../Types/user_types";

const roles = Object.keys(UserRoleDef)
	.map(k => UserRoleDef[k])
	.map(v => ({
		id: v,
		name: v,
	}));
roles.unshift({
	id: "",
	name: "",
});


const ruleUpdatePaths = {
	[WaitingTypes.add]: (state: SimpleStoreShape<User>, payload: ActionRule) => {
		const roles = [...state.data.roles, payload]
			.sort(keyedSortFn("name"));
		return {
			...state,
			data: {
				...state.data,
				roles: roles,
			},
		};
	},
	[WaitingTypes.remove]: (
		state: SimpleStoreShape<User>,
		payload: { key: number | string}
	) => {
		const { key } = payload;
		const roles = [...state.data.roles];
		const idx = roles.findIndex(r => r.name === key);
		roles.splice(idx, 1);
		return {
			...state,
			data: {
				...state.data,
				roles: roles,
			},
		};
	},
};

export const SiteUserRoleAssignmentTable = () => {

	const [state, dispatch] = useDataWaitingReducer(
		new RequiredDataStore<User>(
			{ id: 0, username: "", roles: [], email: ""}
		),
		{
			reducerMods: ruleUpdatePaths,
			middleware: [globalStoreLogger("path users")],
		}
	);
	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const { enqueueSnackbar } = useSnackbar();
	const location = useLocation();
	const { subjectuserkey } = useParams();

	const { callStatus } = state;

	useEffect(() => {
		document.title =
			"Musical Chairs - Site Users";
	},[]);

	useEffect(() => {
		if (!subjectuserkey) {
			enqueueSnackbar("No user selected", { variant: "error"});
			return;
		}
		const requestObj = fetchUser({ subjectuserkey });
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;

			dispatch(dispatches.started());
			try {
				const data = await requestObj.call();
				dispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);

			}
			catch (err) {
				const errMsg = formatError(err);
				enqueueSnackbar(errMsg, { variant: "error"});
				dispatch(dispatches.failed(errMsg));
			}

		};
		fetch();
		return () => requestObj.abortController.abort();
	},[
		dispatch,
		subjectuserkey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
		enqueueSnackbar,
	]);

	const addRole = async (rule: ActionRuleCreationInfo, user: User) => {
		try {
			const requestObj = addSiteUserRule({
				subjectuserkey: user.id,
				rule,
			});
			const addedRule = await requestObj.call();
			dispatch(dispatches.add(addedRule));
			enqueueSnackbar("Role added!", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	const removeRole = async (role: ActionRule, user: User) => {
		try {
			const requestObj = removeSiteUserRule({
				subjectuserkey: user.id,
				rulename: role.name,
			});
			await requestObj.call();
			dispatch(dispatches.remove(role.name));
			enqueueSnackbar(`${role.name} removed!`, { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};


	return (
		<>
			<h1>
				Site Users
			</h1>
			<Box m={1}>
			</Box>
			<Loader
				status={callStatus}
				error={state.error}
			>
				<UserRoleAssignmentTable
					users={state.data ? [state.data] : []}
					removeRole={removeRole}
					addRole={addRole}
					availableRoles={roles}
				/>
			</Loader>
		</>
	);
};


