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
import { Link, useParams, useLocation } from "react-router-dom";
import { 
	useHasAnyRoles,
} from "../../Context_Providers/AuthContext/AuthContext";
import {
	useStationData,
} from "../../Context_Providers/AppContext/AppContext";
import { 
	Calls,
} from "../../API_Calls/stationCalls";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import { getListenAddress } from "../../Helpers/request_helpers";
import {
	useKeyedVoidWaitingReducer,
	keyedVoidDispatches as dispatches,
} from "../../Reducers/keyedVoidWaitingReducer";
import { CallStatus, StationTypes } from "../../constants";
import { YesNoControl } from "../Shared/YesNoControl";
import { userKeyMatch } from "../../Helpers/compare_helpers";
import {
	anyConformsToAnyRule,
} from "../../Helpers/rule_helpers";
import { StationInfo } from "../../Types/station_types";
import { IdValue } from "../../Types/generic_types";
import { ButtonClickEvent } from "../../Types/browser_types";




export const Stations = () => {

	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		update: updateStation,
	} = useStationData();

	const [toggleState, toggleDispatch] = useKeyedVoidWaitingReducer();

	const pathVars = useParams();
	const location =  useLocation();
	const canCreateStation = useHasAnyRoles([UserRoleDef.STATION_CREATE]);
	const canEnableStation = useHasAnyRoles([UserRoleDef.STATION_FLIP]);
	const { enqueueSnackbar } = useSnackbar();
	const [ waitConfirm, setWaitConfirm ] = useState("");

	const disableAllStations = async () => {
		const ids = stations.map(s => s.id);
		try {
			toggleDispatch(dispatches.started(ids));
			const requestObj = Calls.disableStations({ includeAll: true });
			await requestObj.call();
			toggleDispatch(dispatches.done(ids));
			enqueueSnackbar("All stations are being disabled", { variant: "success"});
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(
				dispatches.failed(
					ids.map(id => ({ key: id, msg: formattedError}))
				)
			);
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const handleDisableStation = async (
		e: ButtonClickEvent,
		station: StationInfo
	) => {
		e.stopPropagation();
		try {
			
			toggleDispatch(dispatches.started([station.id]));
			const requestObj = Calls.disableStations({ ids: [station.id]});
			await requestObj.call();
			toggleDispatch(dispatches.done([station.id]));
			enqueueSnackbar(
				`${station.name} is being disabled`, { variant: "success"}
			);
			updateStation({...station, isrunning: false});
			setWaitConfirm("");
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(dispatches.failed([{
				key: station.id,
				msg: formattedError,
			}]));
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const handleEnableStation = async (
		e: ButtonClickEvent,
		station: StationInfo
	) => {
		e.stopPropagation();
		try {
			toggleDispatch(dispatches.started([station.id]));
			const requestObj = Calls.enableStation({ ids: station.id});
			const enabledStations = await requestObj.call();
			if (enabledStations.some(s => s.id === station.id)) {
				toggleDispatch(dispatches.done([station.id]));
				enqueueSnackbar(
					`${station.displayname} is being enabled`, { variant: "success"}
				);
				updateStation({...station, isrunning: true});
			}
			else {
				toggleDispatch(
					dispatches.failed([{
						key: station.id,
						msg: `${station.displayname} could not be enabled`,
					}])
				);
				enqueueSnackbar(
					`${station.displayname} could not be enabled`, {variant: "error" }
				);
			}
		}
		catch(err) {
			const formattedError = formatError(err);
			toggleDispatch(
				dispatches.failed([{
					key: station.id,
					msg: formattedError,
				}])
			);
			enqueueSnackbar(formattedError, {variant: "error" });
		}
	};

	const canToggleStation = (id?: IdValue) => {
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

	const stations = contextStations && pathVars.ownerkey ?
		contextStations.filter(s =>
			!!s.owner && !!pathVars.ownerkey &&
			userKeyMatch(pathVars.ownerkey, s.owner)
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

				const catalogueRoute = s.typeid === StationTypes.SONGS_ONLY ? 
					DomRoutes.songCatalogue :
					DomRoutes.collectionCatalogue;

				return (<Accordion
					key={`station_${idx}`}
					defaultExpanded={false}
					square
				>
					<AccordionSummary
						expandIcon={<ExpandMoreIcon />}
					>
						<span>
							{s.displayname || s.name} -
							{waitConfirm === s.name ?
								<YesNoControl
									message={`Disable ${s.displayname}?`}
									onYes={(e) => handleDisableStation(e, s)}
									onNo={() => setWaitConfirm("")}
								/> :
								<Button
									onClick={e => s.isrunning ?
										openDisableConfirm(e, s.name) :
										handleEnableStation(e, s)
									}
									disabled={!canToggleStation(s.id)}
								>
									{s.isrunning ? "Online!": "Offline"}
								</Button>
							}
						</span>
						<Typography>
							<Button
								onClick={e => e.stopPropagation()}
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
										to={`${catalogueRoute({
											stationkey: s.name,
											ownerkey: s.owner?.username || "",
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
											stationkey: s.name,
											ownerkey: s.owner?.username || "",
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
												stationkey: s.name,
												ownerkey: s.owner?.username || "",
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
											stationkey: s.name,
											ownerkey: s.owner?.username || "",
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
											stationkey: s.name,
											ownerkey: s.owner?.username || "",
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

export default Stations;