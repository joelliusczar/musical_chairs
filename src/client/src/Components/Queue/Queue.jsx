import React, { useEffect, useState, useReducer } from "react";
import { useHistory, useLocation, Link } from "react-router-dom";
import { fetchQueue } from "../../API_Calls/stationCalls";
import { MenuItem,
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Typography,
	TextField,
	Box,
	Select,
	Pagination,
	PaginationItem,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import Loader from "../Shared/Loader";
import { DomRoutes } from "../../constants";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import {
	waitingReducer,
	pageableDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import {
	urlBuilderFactory,
	getRowsCount,
	getPageCount,
} from "../../Helpers/pageable_helpers";

const useStyles = makeStyles(() => ({
	select: {
		width: 150,
	},
}));

const queueInitialState = {
	...pageableDataInitialState,
	data: {...pageableDataInitialState.data,
		nowPlaying: {
			name: "",
			album: "",
			artist: "",
		},
	},
};

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

export const Queue = () => {

	const {
		items: stations,
	} = useStationData();

	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const page = parseInt(queryObj.get("page") || "1");
	const stationNameFromQS = queryObj.get("name") || "";

	const [currentQueryStr, setCurrentQueryStr] = useState("");

	const urlHistory = useHistory();
	const classes = useStyles();

	const [queueState, queueDispatch] =
		useReducer(waitingReducer(), queueInitialState);

	const { callStatus: queueCallStatus } = queueState;

	const getPageUrl = urlBuilderFactory(DomRoutes.queue);

	useEffect(() => {
		document.title = `Musical Chairs - Queue${`- ${stationNameFromQS || ""}`}`;
	},[stationNameFromQS]);


	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === location.search) return;
			const queryObj = new URLSearchParams(location.search);
			const stationNameFromQS = queryObj.get("name");
			if (!stationNameFromQS) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			queueDispatch(dispatches.started());
			try {
				const data = await fetchQueue({
					station: stationNameFromQS,
					params: { page: page - 1, limit: limit } }
				);
				queueDispatch(dispatches.done(data));
				setCurrentQueryStr(location.search);
			}
			catch (err) {
				queueDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
	},[
		queueDispatch,
		fetchQueue,
		location.search,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>Queue: {stationNameFromQS}</h1>
			{stations?.length > 0 && (
				<Box m={1}>
					<TextField
						select
						className={classes.select}
						label="Stations"
						onChange={(e) => {
							urlHistory.replace(getPageUrl(
								{ name: e.target.value },
								location.search
							));
						}}
						value={stationNameFromQS?.toLowerCase() || ""}
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
				</Box>)}
			<Box m={1}>
				<Loader
					status={queueCallStatus}
					error={queueState.error}
				>
					<Typography>Now Playing</Typography>
					<Typography>
						{formatNowPlaying(queueState?.data?.nowPlaying)}
					</Typography>
					{queueState?.data?.items?.length > 0 ? <>
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
									{queueState.data?.items?.map((item, idx) => {
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
						<Box m={1}>
							<Select
								displayEmpty
								defaultValue={50}
								label="Row Count"
								onChange={(e) => {
									urlHistory.replace(
										getPageUrl(
											{ rows: e.target.value, page: 1 },
											location.search
										)
									);
								}}
								renderValue={(v) => v || "Select Row Count"}
								value={getRowsCount(location.search)}
							>
								{[10, 50, 100, 1000].map((size) => {
									return (<MenuItem key={`size_${size}`} value={size}>
										{size}
									</MenuItem>);
								})}
							</Select>
							<Pagination
								count={getPageCount(
									location.search,
									queueState.data?.totalRows
								)}
								page={page}
								renderItem={item => {
									return (<PaginationItem
										component={Link}
										to={getPageUrl({ page: item.page }, location.search)}
										{...item} />);
								} }
								sx={{}} />
						</Box>
					</> :
						<Typography>No records</Typography>}
				</Loader>
			</Box>
		</>
	);
};
