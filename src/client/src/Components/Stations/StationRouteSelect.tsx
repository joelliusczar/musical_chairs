import React, { useEffect, useState, useMemo } from "react";
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

	const { getPageUrl, onChange, unrendered } = props;
	const pathVars = useParams();
	const urlHistory = useHistory();
	const location = useLocation();

	const {
		items: contextStations,
	} = useStationData();

	const stations = useMemo(() => contextStations ?
		contextStations.filter(s => userKeyMatch(pathVars.ownerKey,s.owner)) :
		contextStations,
	[contextStations, pathVars.ownerKey]
	);

	const pathToStation = (path) => {
		const split = path.split("/");
		const selectedStations = stations?.filter(
			s => keyMatch(split[1], s) &&
				userKeyMatch(split[0],s.owner)
		);
		if (selectedStations.length === 1) {
			return selectedStations[0];
		}
		else if (selectedStations.length === 2) {
			//if there is an ambiguity, we'll prefer the matching name
			const nameMatches = selectedStations
				.filter(s => s.name?.toLowerCase() === split[1]);
			if (nameMatches.length == 1) {
				return nameMatches[0];
			}
			//I can't think of a situation where this would actually hit
			const idMatches = selectedStations
				.filter(s => s.id?.toString() === split[1]);
			if (idMatches.length == 1) {
				return idMatches[0];
			}
		}
		return null;
	};

	const pathSuffix = useMemo(() =>
		`${pathVars.ownerKey}/${pathVars.stationKey?.toLowerCase()}`,
	[pathVars.ownerKey,pathVars.stationKey]
	);

	const [selectedStation, setSelectedStation] = useState(pathToStation(
		pathSuffix
	));

	useEffect(() => {
		const station = pathToStation(pathSuffix);
		setSelectedStation(station);
		onChange && onChange(station);
	},[setSelectedStation, pathSuffix, stations]);

	const stationName = selectedStation?.name?.toLowerCase() || "";
	const ownername = selectedStation?.owner?.username?.toLowerCase() || "";


	return (stations?.length > 0 && !unrendered &&
		<TextField
			select
			SelectProps={{
				renderValue: () => {
					return selectedStation?.displayName || selectedStation?.name || "";
				},
			}}
			label="Stations"
			onChange={(e) => {
				const station = pathToStation(e.target.value);
				onChange && onChange(station);
				setSelectedStation(station);
				urlHistory.replace(getPageUrl(
					{
						ownerKey: station?.owner?.username?.toLowerCase(),
						stationKey: station?.name?.toLowerCase(),
					},
					location.search)
				);
			}}
			value={
				`${ownername}/${stationName}`
			}
		>
			<ListSubheader>
				<Grid container className="station-menu">
					<Grid item xs={6} className="station-menu">Station</Grid>
					<Grid item xs={6} className="station-menu">Owner</Grid>
				</Grid>
			</ListSubheader>
			<MenuItem key="empty_station" value={"/"}>
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
							{s.displayName || s.name}
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
	onChange: PropTypes.func,
	unrendered: PropTypes.bool,
};