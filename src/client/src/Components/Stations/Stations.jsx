import React, { useEffect, useReducer } from "react";
import {
	Accordion,
	AccordionSummary,
	AccordionDetails,
	Button,
	Chip,
	Grid,
	Tooltip,
	Typography,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import Loader from "../Shared/Loader";
import { fetchStations } from "./stationService";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { DomRoutes } from "../../constants";
import { Link, useLocation } from "react-router-dom";
import {
	waitingReducer,
	listDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";


const useStyles = makeStyles(() => ({
	buttons: {
		marginRight: 10,
	},
}));


export default function Stations(){
	const [state, dispatch] = useReducer(waitingReducer(), listDataInitialState);
	const { callStatus } = state;
	const location = useLocation();
	const classes = useStyles();

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
						<Typography>{s.name}</Typography>
					</AccordionSummary>
					<AccordionDetails>
						<div>
							<Grid container>
								<Grid item>
									<Tooltip
										title={`${DomRoutes.songCatalogue}${s.name}`}
									>
										<Button
											component={Link}
											color="primary"
											variant="contained"
											className={classes.buttons}
											to={`${DomRoutes.songCatalogue}${s.name}`}
										>
												Song Catalogue
										</Button>
									</Tooltip>
								</Grid>
								<Grid item>

									<Tooltip title={`${DomRoutes.history}${s.name}`}>
										<Button
											component={Link}
											color="primary"
											variant="contained"
											className={classes.buttons}
											to={`${DomRoutes.history}${s.name}`}
										>
												Song History
										</Button>
									</Tooltip>
								</Grid>
								<Grid item>
									<Tooltip title={`${DomRoutes.queue}${s.name}`}>
										<Button
											component={Link}
											color="primary"
											variant="contained"
											className={classes.buttons}
											to={`${DomRoutes.queue}${s.name}`}
										>
												Song Queue
										</Button>
									</Tooltip>
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