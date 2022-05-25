import React, { useEffect } from "react";
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
import { fetchStations } from "./stations_slice";
import { useDispatch, useSelector } from "react-redux";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { CallStatus, DomRoutes, CallType } from "../../constants";
import { Link, useLocation } from "react-router-dom";

const useStyles = makeStyles(() => ({
	buttons: {
		marginRight: 10,
	},
}));

export default function Stations(){

	const location = useLocation();

	const stationsStatus =	useSelector((appState) => 
		appState.stations.status)[CallType.fetch];
	const stationsError =	useSelector((appState) => 
		appState.stations.error[CallType.fetch]);
	const stationsObj = useSelector((appState) => 
		appState.stations.values[CallType.fetch]);
	const dispatch = useDispatch();
	const classes = useStyles();

	useEffect(() => {
		document.title = "Musical Chairs - Stations";
	},[location]);

	useEffect(() => {
		if(!stationsStatus || stationsStatus === CallStatus.idle) { 
			dispatch(fetchStations());
		}
	}, [dispatch, stationsStatus]);

	return (<>
		<h1>Stations</h1>
		<Loader
			status={stationsStatus}
			error={stationsError}
			isReady
		>
			{stationsObj.items.map((s, idx) => {
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
			})}
		</Loader>
	</>);
}