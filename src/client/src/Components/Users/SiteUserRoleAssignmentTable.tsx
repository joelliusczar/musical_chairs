import React, { useEffect, useState, useReducer } from "react";
import {
	Box,
} from "@mui/material";
import {
	waitingReducer,
	dispatches,
	initialState,
	waitingTypes,
	globalStoreLogger,
} from "../Shared/waitingReducer";
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
import { useParams } from "react-router-dom";

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
	[waitingTypes.add]: (state, payload) => {
		const roles = [...state.data.roles, payload]
			.sort(keyedSortFn("username"));
		return {
			...state,
			data: {
				...state.data,
				roles: roles,
			},
		};
	},
	[waitingTypes.remove]: (state, payload) => {
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

	const [state, dispatch] = useReducer(
		waitingReducer(ruleUpdatePaths, [globalStoreLogger("path users")]),
		initialState
	);
	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const { enqueueSnackbar } = useSnackbar();
	const { subjectUserKey } = useParams();

	const { callStatus } = state;

	useEffect(() => {
		document.title =
			"Musical Chairs - Site Users";
	},[]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;

			dispatch(dispatches.started());
			try {
				const data = await fetchUser({ subjectUserKey });
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
		subjectUserKey,
		fetchUser,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	const addRole = async (rule, user) => {
		try {
			const addedRule = await addSiteUserRule({
				subjectUserKey: user.id,
				rule,
			});
			dispatch(dispatches.add(addedRule));
			enqueueSnackbar("Role added!", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	const removeRole = async (role, user) => {
		try {
			await removeSiteUserRule({
				subjectUserKey: user.id,
				params: {
					ruleName: role.name,
				},
			});
			dispatch(dispatches.remove(role));
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

SiteUserRoleAssignmentTable.propTypes = {
};

