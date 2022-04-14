import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { fetchStations } from "../Stations/stations_slice";
import { fetchQueue } from "./queue_slice";
import { useDispatch, useSelector } from "react-redux";
import { makeStyles, 
	MenuItem, 
	Select, 
	Table, 
	TableBody, 
	TableContainer, 
	TableCell, 
	TableHead, 
	TableRow, 
	Typography,
} from "@material-ui/core";
import Loader from "../Shared/Loader";
import { CallStatus, DomRoutes, CallType } from "../../constants";

const useStyles = makeStyles(() => ({
	select: {
		width: 150,
	},
}));

/*
						yield { 
								'id': row[0],
								'song': tag.title, 
								'album': tag.album,
								'artist': tag.artist,
								'lastPlayedTimestamp': row[2]
						}
				except:
						yield {
								'id': row[0],
								'lastPlayedTimestamp': row[2]
						}
*/
const formatNowPlaying = (nowPlaying) => {
	if(!nowPlaying) return "No song info available";
	const song = nowPlaying.name || "{No song name}";
	const album = nowPlaying.album || "{No album name}";
	const artist = nowPlaying.artist || "{No artist name}";
	const str = `Song: ${song} - ${album} - ${artist}`;
	return str;
};

export default function Queue() {
	const [selectedStation, setSelectedStation] = useState("");
	const [selectTouched, setSelectTouched] = useState();
	const { station: stationParam } = useParams();
	const history = useHistory();
	const dispatch = useDispatch();
	const classes = useStyles();
	const stations = useSelector((appState) => 
		appState.stations.values[CallType.fetch]);
	const stationsStatus =	useSelector((appState) => 
		appState.stations.status[CallType.fetch]);
	const queueItems = useSelector((appState) => 
		appState.queue.values[CallType.fetch]);
	const queueItemsStatus =	useSelector((appState) => 
		appState.queue.status[CallType.fetch]);
	const queueItemsError =	useSelector((appState) => 
		appState.queue.error[CallType.fetch]);

	useEffect(() => {
		if(!stationsStatus || stationsStatus === CallStatus.idle) { 
			dispatch(fetchStations());
		}
	}, [dispatch, stationsStatus]);

	useEffect(() => {
		document.title = `Musical Chairs - Queue${`- ${stationParam || ""}`}`;
	},[stationParam]);

	useEffect(() => {
		if(!selectTouched) return;
		history.replace(`${DomRoutes.queue}${selectedStation}`);
	}, [history, selectedStation, selectTouched]);

	useEffect(() => {
		if (!stationParam) return;
		const station = stationParam.toLowerCase();
		if(stations.items.some(s => s.name.toLowerCase() === station)) {
			setSelectedStation(stationParam);
			setSelectTouched(false);
			dispatch(fetchQueue({ station: stationParam }));
		}
	}, [stationParam, dispatch,setSelectedStation, setSelectTouched, stations]);

	return (
		<>
			<h1>Queue: {stationParam}</h1>
			{stations && (
				<Select
					name="station-select"
					className={classes.select}
					displayEmpty
					label="Stations"
					onChange={(e) => {
						setSelectTouched(true);
						setSelectedStation(e.target.value);
					}}
					renderValue={(v) => v || "Select Station"}
					value={selectedStation}
				>
					{stations.items.map((s) => {
						return (
							<MenuItem key={s.name} value={s.name}>
								{s.name}
							</MenuItem>
						);
					})}
				</Select>
			)}
			<Loader 
				status={queueItemsStatus} 
				error={queueItemsError} 
				isReady={!!stationParam}
			>
				<Typography>Now Playing</Typography>
				<Typography>
					{formatNowPlaying(queueItems.nowPlaying)}
				</Typography>
				<TableContainer>
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell>Song</TableCell>
								<TableCell>Album</TableCell>
								<TableCell>Artist</TableCell>
								<TableCell>Added</TableCell>
								<TableCell>Requested</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{queueItems.items.map((item, idx) => {
								return (
									<TableRow key={`song_${idx}`}>
										<TableCell>
											{item.name || "{No song name}"}
										</TableCell>
										<TableCell>
											{item.album || "{No album name}"}
										</TableCell>
										<TableCell>
											{item.artist || "{No artist name}"}
										</TableCell>
										<TableCell></TableCell>
										<TableCell></TableCell>
									</TableRow>
								);
							})}
						</TableBody>
					</Table>
				</TableContainer>
			</Loader>
		</>
	);
}
