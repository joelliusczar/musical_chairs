import React from "react";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import { MenuItem, TextField } from "@mui/material";
import { useHistory, useLocation, useParams } from "react-router-dom";
import PropTypes from "prop-types";
import { makeStyles } from "@mui/styles";

const useStyles = makeStyles(() => ({
	select: {
		width: 150,
	},
}));

export const StationSelect = (props) => {

	const { getPageUrl } = props;
	const {
		items: stations,
	} = useStationData();

	const urlHistory = useHistory();
	const location = useLocation();
	const pathVars = useParams();


	const classes = useStyles();

	return (stations?.length > 0 &&
		<TextField
			select
			className={classes.select}
			label="Stations"
			onChange={(e) => {
				urlHistory.replace(getPageUrl(
					{
						stationKey: e.target.value,
						ownerKey: pathVars.ownerKey,
					},
					location.search)
				);
			}}
			value={pathVars.stationKey?.toLowerCase() || ""}
		>
			<MenuItem key="empty_station" value={""}>
					Select a Station
			</MenuItem>
			{stations.map((s) => {
				return (
					<MenuItem key={s.name} value={s.name?.toLowerCase()}>
						{s.displayName}
					</MenuItem>
				);
			})}
		</TextField>
	);
};

StationSelect.propTypes = {
	getPageUrl: PropTypes.func,
};