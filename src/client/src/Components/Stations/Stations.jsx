import React, { useEffect } from "react";
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
import { Link, useLocation } from "react-router-dom";
import { UserRoleDef } from "../../constants";
import { useHasAnyRoles } from "../../Context_Providers/AuthContext";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import { enableStations, disableStations } from "../../API_Calls/stationCalls";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";


const useStyles = makeStyles(() => ({
	buttons: {
		marginRight: 10,
	},
}));


export const Stations = () => {

	const {
		items: stations,
		callStatus: stationCallStatus,
		error: stationError,
	} = useStationData();

	const location = useLocation();
	const classes = useStyles();
	const canEditStation = useHasAnyRoles([UserRoleDef.STATION_EDIT]);
	const canEnableStation = useHasAnyRoles([UserRoleDef.STATION_FLIP]);
	const { enqueueSnackbar } = useSnackbar();

	const disableAllStations = async () => {
		try {
			await disableStations({ names: "*"});
			enqueueSnackbar("All stations are being disabled", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	useEffect(() => {
		document.title = "Musical Chairs - Stations";
	},[location]);

	return (<>
		<Typography variant="h1">Stations</Typography>
		<Button
			component={Link}
			to={DomRoutes.stationsEdit}
		>
			Add New Station
		</Button>
		<Button
			onClick={disableAllStations}
		>
			Disable All Stations
		</Button>
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
							{s.displayName || s.name} - {s.isRunning? "Online!": "Offline"}
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
										to={`${DomRoutes.stationsEdit}?id=${s.id}`}
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
										to={`${DomRoutes.songCatalogue}?name=${s.name}`}
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
										to={`${DomRoutes.history}?name=${s.name}`}
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
										to={`${DomRoutes.queue}?name=${s.name}`}
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