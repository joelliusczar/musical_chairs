import React from "react";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import {
	MenuItem,
	TextField,
	ListSubheader,
	Grid,
} from "@mui/material";
import { useHistory, useLocation, useParams } from "react-router-dom";
import PropTypes from "prop-types";
import { userKeyMatch, keyMatch } from "../../Helpers/compare_helpers";


export const StationRouteSelect = (props) => {

	const { getPageUrl } = props;
	const {
		items: contextStations,
	} = useStationData();

	const urlHistory = useHistory();
	const location = useLocation();
	const pathVars = useParams();

	const stations = contextStations ?
		contextStations.filter(s => userKeyMatch(pathVars.ownerKey,s.owner)) :
		contextStations;


	return (stations?.length > 0 &&
		<TextField
			select
			SelectProps={{
				renderValue: e => {
					const split = e.split("/");
					const selectedStation = stations?.filter(
						s => keyMatch(split[1], s) &&
							userKeyMatch(split[0],s.owner)
					);
					if (selectedStation) {
						return selectedStation[0].displayName;
					}
					return "";
				},
			}}
			label="Stations"
			onChange={(e) => {
				const split = e.target.value.split("/");
				urlHistory.replace(getPageUrl(
					{
						ownerKey: split[0],
						stationKey: split[1],
					},
					location.search)
				);
			}}
			value={
				`${pathVars.ownerKey}/${pathVars.stationKey?.toLowerCase()}` || ""
			}
		>
			<ListSubheader>
				<Grid container className="station-menu">
					<Grid item xs={6} className="station-menu">Station</Grid>
					<Grid item xs={6} className="station-menu">Owner</Grid>
				</Grid>
			</ListSubheader>
			<MenuItem key="empty_station" value={""}>
			</MenuItem>
			{stations.map((s) => {
				return (
					<MenuItem
						key={s.name}
						value={`${s.owner?.username}/${s.name?.toLowerCase()}`}
						container
						component={Grid}
						className="station-menu"
					>
						<Grid item xs={6} className="station-menu">
							{s.displayName}
							{/* <Typography noWrap >
							</Typography> */}
						</Grid>
						<Grid item xs={6} className="station-menu">
							{s.owner?.username}
							{/* <Typography>
							</Typography> */}
						</Grid>
					</MenuItem>
				);
			})}
		</TextField>
	);
};

StationRouteSelect.propTypes = {
	getPageUrl: PropTypes.func,
};