import React, { useEffect, useReducer, useState } from "react";
import {
	Accordion,
	AccordionSummary,
	AccordionDetails,
	Button,
	Grid,
	Typography,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import Loader from "../Shared/Loader";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { DomRoutes } from "../../constants";
import { Link, useLocation, useParams } from "react-router-dom";
import { UserRoleDef } from "../../constants";
import { useHasAnyRoles } from "../../Context_Providers/AuthContext";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import { enableStations, disableStations } from "../../API_Calls/stationCalls";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import { getListenAddress } from "../../Helpers/url_helpers";
import {
	waitingReducer,
	dispatches,
	keyedWaitingReducerMap,
} from "../Shared/waitingReducer";
import { CallStatus } from "../../constants";
import { YesNoControl } from "../Shared/YesNoControl";
import { userKeyMatch } from "../../Helpers/compare_helpers";


const useStyles = makeStyles(() => ({
	buttons: {
		marginRight: 10,
	},
}));


export const Stations = () => {

	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		update: updateStation,
	} = useStationData();

	const [toggleState, toggleDispatch] = useReducer(
		waitingReducer(keyedWaitingReducerMap), {}
	);

	const location = useLocation();
	const pathVars = useParams();
	const classes = useStyles();
	const canEditStation = useHasAnyRoles([UserRoleDef.STATION_EDIT]);
	const canEnableStation = useHasAnyRoles([UserRoleDef.STATION_FLIP]);
	const { enqueueSnackbar } = useSnackbar();
	const [ waitConfirm, setWaitConfirm ] = useState("");

	const disableAllStations = async () => {
		try {
			toggleDispatch(dispatches.started({ key: "*" }));
			await disableStations({ names: "*"});
			toggleDispatch(dispatches.done({ key: "*" }));
			enqueueSnackbar("All stations are being disabled", { variant: "success"});
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(dispatches.failed({key: "*", data: formattedError}));
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const handleDisableStation = async (e, id, name) => {
		e.stopPropagation();
		try {
			toggleDispatch(dispatches.started({ key: id }));
			await disableStations({ ids: id});
			toggleDispatch(dispatches.done({ key: id }));
			enqueueSnackbar(`${name} is being disabled`, { variant: "success"});
			updateStation(id, p => ({...p, isRunning: false}));
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(dispatches.failed({key: id, data: formattedError}));
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const handleEnableStation = async (e, id, name) => {
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

	const canToggleStation = (id) => {
		if(toggleState[id]?.callStatus === CallStatus.loading ||
			toggleState["*"]?.callStatus === CallStatus.loading
		) {
			return false;
		}
		return true;
	};

	const openDisableConfirm = (e, name) => {
		e.stopPropagation();
		setWaitConfirm(name);
	};

	const stations = contextStations && pathVars.ownerKey ?
		contextStations.filter(s => userKeyMatch(pathVars.ownerKey,s.owner)) :
		contextStations;

	useEffect(() => {
		document.title = "Musical Chairs - Stations";
	},[location]);

	return (<>
		<Typography variant="h1">Stations</Typography>
		{canEditStation && <Button
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
			{stations?.length ? stations.map((s, idx) => {
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
								href={getListenAddress(s.name)}
							>
								Listen
							</Button>
						</Typography>
					</AccordionSummary>
					<AccordionDetails>
						<div>
							<Grid container>
								<Grid item>
									{canEditStation && <Button
										color="primary"
										variant="contained"
										component={Link}
										to={DomRoutes.stationsEdit({
											stationKey: s.name,
											ownerKey: s.owner?.username,
										})}
									>
										Edit
									</Button>}
								</Grid>
								<Grid item>
									<Button
										component={Link}
										color="primary"
										variant="contained"
										className={classes.buttons}
										to={`${DomRoutes.songCatalogue({
											stationKey: s.name,
											ownerKey: s.owner?.username,
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
										className={classes.buttons}
										to={`${DomRoutes.history({
											stationKey: s.name,
											ownerKey: s.owner?.username,
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
										className={classes.buttons}
										to={`${DomRoutes.queue(
											{
												stationKey: s.name,
												ownerKey: s.owner?.username,
											}
										)}`}
									>
											Song Queue
									</Button>
								</Grid>
							</Grid>
						</div>
					</AccordionDetails>
				</Accordion>);
			}) : <Typography>No Stations have been added</Typography>}
		</Loader>
	</>);
};