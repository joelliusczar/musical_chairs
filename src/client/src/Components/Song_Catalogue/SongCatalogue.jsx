import React, { useEffect, useState } from "react";
import { useHistory, useParams, useLocation, Link } from "react-router-dom";
import { fetchStations } from "../Stations/stationService";
import { fetchSongCatalogue } from "./song_catalogue_slice";
import { useDispatch, useSelector } from "react-redux";
import { MenuItem,
	Select,
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Button,
	Pagination,
	PaginationItem,
	Box,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import Loader from "../Shared/Loader";
import { CallStatus, DomRoutes, CallType } from "../../constants";
import { requestSong } from "../Stations/song_request_slice";


const useStyles = makeStyles(() => ({
	select: {
		width: 150,
	},
}));

export default function SongCatalogue() {
	const [selectedStation, setSelectedStation] = useState("");
	const [selectTouched, setSelectTouched] = useState();
	const { station: stationParam } = useParams();
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const page = parseInt(queryObj.get("page") || "1");
	const urlHistory = useHistory();
	const dispatch = useDispatch();
	const classes = useStyles();
	const stations = useSelector((appState) =>
		appState.stations.values[CallType.fetch]);
	const stationsStatus =	useSelector((appState) =>
		appState.stations.status[CallType.fetch]);
	const songCatalogueObj = useSelector((appState) =>
		appState.songCatalogue.values[CallType.fetch]);
	const songCatalogueStatus =	useSelector((appState) =>
		appState.songCatalogue.status[CallType.fetch]);
	const songCatalogueError =	useSelector((appState) =>
		appState.songCatalogue.error[CallType.fetch]);

	const dispatchSongRequest = (songId) => {
		dispatch(requestSong({station: stationParam, songId }));
	};

	const getPageUrl = (params) => {
		let queryStr = null;
		if(queryObj) {
			if(params.page) {
				queryObj.set("page", params.page);
			}
			if(params.rows) {
				queryObj.set("rows", params.rows);
			}
			queryStr = `?${queryObj.toString()}`;
		}
		return `${DomRoutes.songCatalogue}${selectedStation}${queryStr}`;
	};

	const getPageCount = () => {
		const rows = parseInt(queryObj.get("rows") || "1");
		const totalRows = songCatalogueObj.totalRows;
		if(rows < 1) {
			return 0;
		}
		return Math.floor(totalRows / rows);
	};

	const getRowsCount = () => {
		return parseInt(queryObj.get("rows") || "50");
	};

	useEffect(() => {
		if(!stationsStatus || stationsStatus === CallStatus.idle) {
			dispatch(fetchStations());
		}
	}, [dispatch, stationsStatus]);

	useEffect(() => {
		document.title =
			`Musical Chairs - Song Catalogue${`- ${stationParam || ""}`}`;
	},[stationParam]);

	useEffect(() => {
		if(!selectTouched) return;
		urlHistory.replace(`${DomRoutes.songCatalogue}${selectedStation}`);
	}, [urlHistory, selectedStation, selectTouched]);

	useEffect(() => {
		if (!stationParam) return;
		const station = stationParam.toLowerCase();
		if(stations.items.some(s => s.name.toLowerCase() === station)) {
			setSelectedStation(stationParam);
			setSelectTouched(false);
			const queryObj = new URLSearchParams(location.search);
			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			dispatch(fetchSongCatalogue({
				station: stationParam,
				params: { page: page - 1, limit: limit } }));
		}
	}, [stationParam,
		dispatch,
		setSelectedStation,
		setSelectTouched,
		stations,
		location.search,
	]);

	return (
		<>
			<h1>SongCatalogue: {stationParam}</h1>
			{stations && (
				<Select
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
				status={songCatalogueStatus}
				error={songCatalogueError}
				isReady={!!stationParam}
			>
				<TableContainer>
					<Table size="small">
						<TableHead>
							<TableRow>
								<TableCell>Song</TableCell>
								<TableCell>Album</TableCell>
								<TableCell>Artist</TableCell>
								<TableCell>Request</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{songCatalogueObj.items.map((item, idx) => {
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
										<TableCell>
											<Button
												color="primary"
												variant="contained"
												onClick={() =>
													dispatchSongRequest(item.id)
												}
											>
												Request
											</Button>
										</TableCell>
									</TableRow>
								);
							})}
						</TableBody>
					</Table>
				</TableContainer>
				<Box sx={{ display: "flex"}}>
					<Select
						displayEmpty
						defaultValue={50}
						label="Row Count"
						onChange={(e) => {
							urlHistory.replace(getPageUrl({ rows: e.target.value, page: 1 }));
						}}
						renderValue={(v) => v || "Select Row Count"}
						value={getRowsCount()}
					>
						{[10, 50, 100, 1000].map((size) => {
							return (<MenuItem key={`size_${size}`} value={size}>
								{size}
							</MenuItem>);
						})}
					</Select>
					<Pagination
						count={getPageCount()}
						page={page}
						renderItem={item => (<PaginationItem
							component={Link}
							to={getPageUrl({page: item.page})}
							{...item}
						/>)}
						sx={{ }}
					/>
				</Box>
			</Loader>
		</>
	);
}
