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
import { fetchUserList } from "./accounts_slice";
import { useCurrentUser } from "./AuthContext";

export const AccountsList = () => {
	const [fetchStatus, setFetchStatus] = useState(null);
	const [fetchError, setFetchError] = useState(null);
	const [tableData, setTableData] = useState({
		items: [],
		totalRows: 0,
	});
	const location = useLocation();

	const currentUser = useCurrentUser();

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
						params: { page: page - 1, pageSize: pageSize },
						currentUser: currentUser,
					});
					setFetchStatus(CallStatus.done);
					setTableData(tableData);
				}
			}
			catch(err) {
				setFetchStatus(CallStatus.failed);
				setFetchError(err.response.data.detail[0].msg);
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
												to={`${DomRoutes.accountsRoles}${item.id}`}
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