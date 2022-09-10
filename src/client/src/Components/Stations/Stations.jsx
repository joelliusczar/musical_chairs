import React, { useEffect, useReducer } from "react";
import {
	Accordion,
	AccordionSummary,
	AccordionDetails,
	Button,
	Chip,
	Grid,
	Typography,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import Loader from "../Shared/Loader";
import { fetchStations } from "../../API_Calls/stationCalls";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { DomRoutes } from "../../constants";
import { Link, useLocation } from "react-router-dom";
import {
	waitingReducer,
	pageableDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { UserRoleDef } from "../../constants";
import { useHasAnyRoles } from "../../Context_Providers/AuthContext";


const useStyles = makeStyles(() => ({
	buttons: {
		marginRight: 10,
	},
}));


export default function Stations(){
	const [state, dispatch] = useReducer(
		waitingReducer(),
		pageableDataInitialState
	);
	const { callStatus } = state;
	const location = useLocation();
	const classes = useStyles();
	const canEditStation = useHasAnyRoles([UserRoleDef.STATION_EDIT]);

	useEffect(() => {
		document.title = "Musical Chairs - Stations";
	},[location]);

	useEffect(() => {
		const fetch = async () => {
			try {
				if(!callStatus) {
					dispatch(dispatches.started());
					const data = await fetchStations();
					dispatch(dispatches.done(data));
				}
			}
			catch(err) {
				dispatch(dispatches.failed(err.response.data.detail[0].msg));
			}
		};

		fetch();
	}, [callStatus, dispatch]);

	return (<>
		<Typography variant="h1">Stations</Typography>
		<Button
			component={Link}
			to={DomRoutes.stationsEdit}
		>
			Add New Station
		</Button>
		<Loader
			status={callStatus}
			error={state.error}
			isReady
		>
			{state.data?.items?.length ? state.data.items.map((s, idx) => {
				return (<Accordion
					key={`station_${idx}`}
					defaultExpanded={false}
					square
				>
					<AccordionSummary
						expandIcon={<ExpandMoreIcon />}
					>
						<Typography>
							{s.displayName || s.name}
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
										to={`${DomRoutes.songCatalogue}${s.name}`}
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
										to={`${DomRoutes.history}${s.name}`}
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
										to={`${DomRoutes.queue}${s.name}`}
									>
											Song Queue
									</Button>
								</Grid>
							</Grid>
							<Typography display="block">Tags:</Typography>
							<div>
								{(s.tags || []).map((t,idx) => {
									return (<Chip
										key={`tag_${idx}`}
										label={t.name}
										className={classes.buttons}
									/>);
								})}
							</div>
						</div>
					</AccordionDetails>
				</Accordion>);
			}) : <Typography>No Stations have been added</Typography>}
		</Loader>
	</>);
}