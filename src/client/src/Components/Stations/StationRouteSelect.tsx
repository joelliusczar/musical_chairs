import React, { useEffect, useState, useMemo, useCallback } from "react";
import {
	useStationData,
} from "../../Context_Providers/AppContext/AppContext";
import {
	MenuItem,
	TextField,
	ListSubheader,
	Box,
} from "@mui/material";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { useSnackbar } from "notistack";
import { userKeyMatch, keyMatch } from "../../Helpers/compare_helpers";
import {
	StationInfo,
	RequiredStationParams,
} from "../../Types/station_types";
import { StationTypes } from "../../constants";

type StationRouteSelectProps = {
	getPageUrl: (
		params: RequiredStationParams,
		currentLocation: string
	) => string,
	onChange?: (s: StationInfo | null) => void,
	unrendered?: boolean,
	stationTypes?: number[],
};

export const StationRouteSelect = (props: StationRouteSelectProps) => {

	const { 
		getPageUrl,
		onChange,
		unrendered,
		stationTypes = [
			StationTypes.SONGS_ONLY,
			StationTypes.ALBUMS_ONLY,
			StationTypes.PLAYLISTS_ONLY,
			StationTypes.ALBUMS_AND_PLAYLISTS,
		],
	} = props;
	const pathVars = useParams();
	const navigate = useNavigate();
	const location = useLocation();
	const { enqueueSnackbar } = useSnackbar();

	const {
		items: contextStations,
	} = useStationData();


	const stations = contextStations.filter(s => 
		stationTypes.some(t => t === s.typeid)
	);

	const pathToStation = useCallback((path: string): StationInfo | null => {
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
	},[stations]);

	const pathSuffix = useMemo(() =>
		`${pathVars.ownerkey}/${pathVars.stationkey?.toLowerCase()}`,
	[pathVars.ownerkey,pathVars.stationkey]
	);

	const [selectedStation, setSelectedStation] = useState(pathToStation(
		pathSuffix
	));

	useEffect(() => {
		const station = pathToStation(pathSuffix);
		setSelectedStation(station);
		!!onChange && onChange(station);
	},[setSelectedStation, pathSuffix, stations, pathToStation, onChange]);

	const stationName = selectedStation?.name?.toLowerCase() || "";
	const ownername = selectedStation?.owner?.username?.toLowerCase() || "";


	return (stations?.length > 0 && !unrendered &&
		<TextField
			select
			SelectProps={{
				renderValue: () => {
					return selectedStation?.displayname || selectedStation?.name || "";
				},
			}}
			label="Stations"
			onChange={(e) => {
				const station = pathToStation(e.target.value);
				!!onChange && onChange(station);
				setSelectedStation(station);
				if (!station || !station.owner) {
					enqueueSnackbar("Invalid station selected.", {variant: "error" });
					return;
				}
				navigate(getPageUrl(
					{
						ownerkey: station?.owner?.username?.toLowerCase(),
						stationkey: station?.name?.toLowerCase(),
					},
					location.search
				),
				{ replace: true}
				);
			}}
			value={
				`${ownername}/${stationName}`
			}
		>
			<ListSubheader>
				<Box className="station-menu">Station</Box>
				<Box className="station-menu">Owner</Box>
			</ListSubheader>
			<MenuItem key="empty_station" value={"/"}>
			</MenuItem>
			{stations.map((s) => {
				return (
					<MenuItem
						key={s.name}
						value={`${s.owner?.username}/${s.name?.toLowerCase()}`}
						className="station-menu"
					>
						<Box className="station-menu">
							{s.displayname || s.name}
							{/* <Typography noWrap >
							</Typography> */}
						</Box>
						<Box className="station-menu">
							{s.owner?.username}
							{/* <Typography>
							</Typography> */}
						</Box>
					</MenuItem>
				);
			})}
		</TextField>
	);
};

