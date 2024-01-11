import React, { useState, useEffect } from "react";
import {
	TableContainer,
	Table,
	TableHead,
	TableRow,
	TableCell,
	TableBody,
	Button,
} from "@mui/material";
import Loader from "../Shared/Loader";
import { CallStatus, DomRoutes } from "../../constants";
import { useLocation, Link } from "react-router-dom";
import { fetchUserList } from "../../API_Calls/userCalls";
import {
	useCurrentUser,
	//useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { User } from "../../Types/user_types";
import {formatError } from "../../Helpers/error_formatter";
import {
	useDataWaitingReducer,
	dataDispatches as dispatches,
} from "../../Reducers/dataWaitingReducer";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	PageableListDataShape,
} from "../../Types/reducerTypes";

export const AccountsList = () => {
	const [state, dispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<User>>(
			{ items: [], totalrows: 0}
		));

	const location = useLocation();

	const currentUser = useCurrentUser();

	useEffect(() => {
		if(currentUser.username) {
			dispatch(dispatches.restart());
		}
	},[currentUser.username, dispatch]);

	useEffect(() => {
		document.title =
			"Musical Chairs - Accounts List";
	},[]);

	useEffect(() => {
		const queryObj = new URLSearchParams(location.search);
		const page = parseInt(queryObj.get("page") || "1");
		const pageSize = parseInt(queryObj.get("rows") || "50");
		const requestObj = fetchUserList({
			params: { page: page - 1, pageSize: pageSize },
		});
		dispatch(dispatches.run((state) => {
			const fetch = async () => {
				const { callStatus } = state;
				try {
					if(!callStatus || callStatus === CallStatus.idle) {
						dispatch(dispatches.started());
						const tableData = await requestObj.call();
						dispatch(dispatches.done(
							tableData
						));
					}
				}
				catch(err) {
					dispatch(dispatches.failed(formatError(err)));
				}

			};
			fetch();
		}));
		return () => requestObj.abortController.abort();
	},[
		dispatch,
		location,
		currentUser,
	]);

	return (
		<>
			<h1>Accounts List</h1>
			<Loader status={state.callStatus} error={state.error}>
				<TableContainer>
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell>Username</TableCell>
								<TableCell>Display Name</TableCell>
								<TableCell>Email</TableCell>
								<TableCell></TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{state.data.items.map((item, idx) => {
								return (
									<TableRow key={`account_${idx}`}>
										<TableCell>{item.username}</TableCell>
										<TableCell>{item.displayname || ""}</TableCell>
										<TableCell>{item.email || ""}</TableCell>
										<TableCell>
											<Button
												component={Link}
												to={DomRoutes.accountsRoles({
													subjectuserkey: item.username,
												})}
											>
												Roles
											</Button>
										</TableCell>
									</TableRow>
								);
							})}
						</TableBody>
					</Table>
				</TableContainer>
			</Loader>
		</>
	);
};