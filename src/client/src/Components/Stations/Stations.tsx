import React, { useEffect, useState } from "react";
import {
	Accordion,
	AccordionSummary,
	AccordionDetails,
	Button,
	Grid,
	Typography,
	Box,
} from "@mui/material";
import Loader from "../Shared/Loader";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { DomRoutes, UserRoleDef } from "../../constants";
import { Link, useLocation, useParams } from "react-router-dom";
import { useHasAnyRoles } from "../../Context_Providers/AuthContext";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import { enableStations, disableStations } from "../../API_Calls/stationCalls";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import { getListenAddress } from "../../Helpers/url_helpers";
import {
	dispatches,
} from "../../Reducers/waitingReducer";
import {
	useVoidKeyedWaitingReducer,
} from "../../Reducers/voidKeyedWaitingReducer";
import { CallStatus } from "../../constants";
import { YesNoControl } from "../Shared/YesNoControl";
import { userKeyMatch } from "../../Helpers/compare_helpers";
import {
	anyConformsToAnyRule,
} from "../../Helpers/rule_helpers";
import { StationInfo } from "../../Types/station_types";
import { IdType } from "../../Types/generic_types";
import { ButtonClickEvent } from "../../Types/browser_types";




export const Stations = () => {

	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		update: updateStation,
	} = useStationData();

	const [toggleState, toggleDispatch] = useVoidKeyedWaitingReducer({});

	const location = useLocation();
	const pathVars = useParams();
	const canCreateStation = useHasAnyRoles([UserRoleDef.STATION_CREATE]);
	const canEnableStation = useHasAnyRoles([UserRoleDef.STATION_FLIP]);
	const { enqueueSnackbar } = useSnackbar();
	const [ waitConfirm, setWaitConfirm ] = useState("");

	const disableAllStations = async () => {
		try {
			toggleDispatch(dispatches.started({ key: "*" }));
			await disableStations({ includeAll: true });
			toggleDispatch(dispatches.done({ key: "*" }));
			enqueueSnackbar("All stations are being disabled", { variant: "success"});
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(dispatches.failed({key: "*", data: formattedError}));
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const handleDisableStation = async (
		e: ButtonClickEvent,
		id: IdType,
		name: string
	) => {
		e.stopPropagation();
		try {
			toggleDispatch(dispatches.started({ key: id }));
			await disableStations({ ids: [id]});
			toggleDispatch(dispatches.done({ key: id }));
			enqueueSnackbar(`${name} is being disabled`, { variant: "success"});
			updateStation(id, p => ({...p, isRunning: false}));
			setWaitConfirm("");
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(dispatches.failed({key: id, data: formattedError}));
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const handleEnableStation = async (
		e: ButtonClickEvent,
		id: IdType,
		name: string
	) => {
		e.stopPropagation();
		try {
			toggleDispatch(dispatches.started({ key: id }));
			await enableStations({ ids: id});
			toggleDispatch(dispatches.done({ key: id }));
			enqueueSnackbar(`${name} is being enabled`, { variant: "success"});
			updateStation(id, p => ({...p, isRunning: true}));
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(dispatches.failed({key: id, data: formattedError}));
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const canToggleStation = (id?: IdType) => {
		if((!!id  && toggleState[id]?.callStatus === CallStatus.loading) ||
			toggleState["*"]?.callStatus === CallStatus.loading
		) {
			return false;
		}
		return true;
	};

	const openDisableConfirm = (e: ButtonClickEvent, name: string) => {
		e.stopPropagation();
		setWaitConfirm(name);
	};

	const canAssignUsersToStation = (station: StationInfo) => {
		const canAssign = anyConformsToAnyRule(
			station.rules,
			[UserRoleDef.STATION_USER_ASSIGN]
		);
		return canAssign;
	};

	const canEditStation = (station: StationInfo) => {
		const canAssign = anyConformsToAnyRule(
			station.rules,
			[UserRoleDef.STATION_EDIT]
		);
		return canAssign;
	};

	const stations = contextStations && pathVars.ownerKey ?
		contextStations.filter(s =>
			!!s.owner && !!pathVars.ownerKey &&
			userKeyMatch(pathVars.ownerKey, s.owner)
		) :
		contextStations;

	useEffect(() => {
		document.title = "Musical Chairs - Stations";
	},[location]);

	return (<>
		<Typography variant="h1">Stations</Typography>
		{canCreateStation && <Button
			component={Link}
			to={DomRoutes.stationsAdd()}
		>
			Add New Station
		</Button>}
		{canEnableStation && (waitConfirm === "*" ?
			<YesNoControl
				message="Disable all stations?"
				onYes={disableAllStations}
				onNo={() => setWaitConfirm("")}
			/> :
			<Button
				onClick={() => setWaitConfirm("*")}
				disabled={!canToggleStation()}
			>
				Disable All Stations
			</Button>
		)}
		<Loader
			status={stationCallStatus}
			error={stationError}
		>
			{stations?.length ? stations.map((s: StationInfo, idx: number) => {
				return (<Accordion
					key={`station_${idx}`}
					defaultExpanded={false}
					square
				>
					<AccordionSummary
						expandIcon={<ExpandMoreIcon />}
					>
						<Typography>
							{s.displayName || s.name} -
							{waitConfirm === s.name ?
								<YesNoControl
									message={`Disable ${s.displayName}?`}
									onYes={(e) => handleDisableStation(e, s.id, s.name)}
									onNo={() => setWaitConfirm("")}
								/> :
								<Button
									onClick={e => s.isRunning ?
										openDisableConfirm(e, s.name) :
										handleEnableStation(e, s.id, s.name)
									}
									disabled={!canToggleStation(s.id)}
								>
									{s.isRunning ? "Online!": "Offline"}
								</Button>
							}
						</Typography>
						<Typography>
							<Button
								component="a"
								href={getListenAddress(s)}
							>
								Listen
							</Button>
						</Typography>
					</AccordionSummary>
					<AccordionDetails>
						<Box>
							<Grid container>
								<Grid item>
									<Button
										component={Link}
										color="primary"
										variant="contained"
										className="station-button"
										to={`${DomRoutes.songCatalogue({
											stationKey: s.name,
											ownerKey: s.owner?.username || "",
										})}`}
									>
											Song Catalogue
									</Button>
								</Grid>
								<Grid item>
									<Button
										component={Link}
										color="primary"
										variant="contained"
										className="station-button"
										to={`${DomRoutes.history({
											stationKey: s.name,
											ownerKey: s.owner?.username || "",
										})}`}
									>
											Song History
									</Button>
								</Grid>
								<Grid item>
									<Button
										component={Link}
										color="primary"
										variant="contained"
										className="station-button"
										to={`${DomRoutes.queue(
											{
												stationKey: s.name,
												ownerKey: s.owner?.username || "",
											}
										)}`}
									>
											Song Queue
									</Button>
								</Grid>
								<Grid item>
									{canEditStation(s) && <Button
										color="primary"
										variant="contained"
										component={Link}
										to={DomRoutes.stationsEdit({
											stationKey: s.name,
											ownerKey: s.owner?.username || "",
										})}
									>
										Edit
									</Button>}
								</Grid>
								<Grid item>
									{canAssignUsersToStation(s) && <Button
										color="primary"
										variant="contained"
										component={Link}
										to={DomRoutes.stationUsers({
											stationKey: s.name,
											ownerKey: s.owner?.username || "",
										})}
									>
										Assign Users
									</Button>}
								</Grid>
							</Grid>
						</Box>
					</AccordionDetails>
				</Accordion>);
			}) : <Typography>No Stations have been added</Typography>}
		</Loader>
	</>);
};