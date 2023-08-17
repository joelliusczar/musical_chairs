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
} from "../../Context_Providers/AuthContext";
import { User } from "../../Types/user_types";
import { TableData } from "../../Types/pageable_types";
import {formatError } from "../../Helpers/error_formatter";

export const AccountsList = () => {
	const [fetchStatus, setFetchStatus] = useState<string | null>(null);
	const [fetchError, setFetchError] = useState<string | null>(null);
	const [tableData, setTableData] = useState<TableData<User>>({
		items: [],
		totalRows: 0,
	});
	const location = useLocation();

	const currentUser = useCurrentUser();

	useEffect(() => {
		if(currentUser.username) {
			setFetchStatus(null);
		}
	},[currentUser.username, setFetchStatus]);

	useEffect(() => {
		document.title =
			"Musical Chairs - Accounts List";
	},[]);

	useEffect(() => {
		const fetch = async () => {
			try {
				if(!fetchStatus || fetchStatus === CallStatus.idle) {
					setFetchStatus(CallStatus.loading);
					const queryObj = new URLSearchParams(location.search);
					const page = parseInt(queryObj.get("page") || "1");
					const pageSize = parseInt(queryObj.get("rows") || "50");
					const tableData = await fetchUserList({
						params: { page: page - 1, pageSize: pageSize }
					});
					setFetchStatus(CallStatus.done);
					setTableData(tableData);
				}
			}
			catch(err) {
				setFetchStatus(CallStatus.failed);
				formatError
				setFetchError(formatError(err));
			}
		};
		fetch();
	},[
		setFetchError,
		fetchStatus,
		setFetchStatus,
		location,
		currentUser,
		setTableData,
	]);

	return (
		<>
			<h1>Accounts List</h1>
			<Loader status={fetchStatus} error={fetchError}>
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
							{tableData.items.map((item, idx) => {
								return (
									<TableRow key={`account_${idx}`}>
										<TableCell>{item.username}</TableCell>
										<TableCell>{item.displayName || ""}</TableCell>
										<TableCell>{item.email || ""}</TableCell>
										<TableCell>
											<Button
												component={Link}
												to={DomRoutes.accountsRoles({
													subjectUserKey: item.username,
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