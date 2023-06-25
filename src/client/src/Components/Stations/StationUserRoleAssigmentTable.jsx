import React, { useEffect, useState, useReducer } from "react";
import {
	Accordion,
	AccordionSummary,
	AccordionDetails,
	Typography,
	Box,
} from "@mui/material";
import {
	waitingReducer,
	dispatches,
	pageableDataInitialState,
} from "../Shared/waitingReducer";
import Loader from "../Shared/Loader";
import {
	fetchStationUsers,
	addStationUserRule,
} from "../../API_Calls/stationCalls";
import { useParams } from "react-router-dom";
import { formatError } from "../../Helpers/error_formatter";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { StationRouteSelect } from "./StationRouteSelect";
import { urlBuilderFactory } from "../../Helpers/pageable_helpers";
import { DomRoutes, UserRoleDef, UserRoleDomain } from "../../constants";
import { UserSearchModalOpener } from "../Accounts/UserSearch";
import { useSnackbar } from "notistack";



export const StationUserRoleAssignmentTable = () => {

	const [state, dispatch] =
		useReducer(waitingReducer(), pageableDataInitialState);
	const [selectedStation, setSelectedStation] = useState();
	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const pathVars = useParams();
	const { enqueueSnackbar } = useSnackbar();

	const { callStatus } = state;

	const getPageUrl = urlBuilderFactory(DomRoutes.history);

	const addUser = async (user) => {
		try {
			const rule = {
				name: UserRoleDef.STATION_VIEW,
				span: 0,
				count: 0,
				priority: null,
				domain: UserRoleDomain.STATION,
			};
			await addStationUserRule({
				stationKey: pathVars.stationKey,
				ownerKey: pathVars.ownerKey,
				rule,
				params: {
					userId: user.id,
				},
			});
			enqueueSnackbar("User added!", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	};

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayName || ""}`;
		document.title =
			`Musical Chairs - Users for ${stationTitle}`;
	},[selectedStation]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			if (!pathVars.stationKey) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			dispatch(dispatches.started());
			try {
				const data = await fetchStationUsers({
					stationKey: pathVars.stationKey,
					ownerKey: pathVars.ownerKey,
					params: { page: page - 1, limit: limit } }
				);
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
		fetchStationUsers,
		pathVars.stationKey,
		pathVars.ownerKey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	const stationName =
		selectedStation?.displayName || selectedStation?.name || "";
	return (
		<>
			<h1>
				Users for station: {stationName}
			</h1>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={getPageUrl}
					onChange={(s) => setSelectedStation(s)}
					unrendered
				/>
				<UserSearchModalOpener
					onConfirm={addUser}
				/>
			</Box>
			<Loader
				status={callStatus}
				error={state.error}
			>
				{state.data?.items?.length && state.data.items.map((u, uidx) => {
					return (<Accordion
						key={`user${uidx}`}
						defaultExpanded={false}
						square
					>
						<AccordionSummary
							expandIcon={<ExpandMoreIcon />}
						>
							<Typography>
								{u.displayName || u.username}
							</Typography>
						</AccordionSummary>
						<AccordionDetails>
							{u.roles?.length && u.roles.map((r, ridx) => {
								return (<Box key={`rule_${uidx}_${ridx}`}>
									{JSON.stringify(r)}
								</Box>);
							})}
						</AccordionDetails>
					</Accordion>);
				})}
			</Loader>
		</>
	);
};

StationUserRoleAssignmentTable.propTypes = {
};

