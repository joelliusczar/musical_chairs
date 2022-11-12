import React, { useEffect, useState, useReducer } from "react";
import { useLocation } from "react-router-dom";
import { fetchQueue } from "../../API_Calls/stationCalls";
import {
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Typography,
	Box,
} from "@mui/material";
import Loader from "../Shared/Loader";
import { DomRoutes } from "../../constants";
import {
	waitingReducer,
	pageableDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { urlBuilderFactory } from "../../Helpers/pageable_helpers";
import { StationSelect } from "../Shared/StationSelect";
import { UrlPagination } from "../Shared/UrlPagination";
import { NowPlaying } from "../Shared/NowPlaying";

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

	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const stationNameFromQS = queryObj.get("name") || "";

	const [currentQueryStr, setCurrentQueryStr] = useState("");

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
			<Box m={1}>
				<StationSelect getPageUrl={getPageUrl} />
			</Box>
			<Box m={1}>
				<Loader
					status={queueCallStatus}
					error={queueState.error}
				>
					<Typography>Now Playing</Typography>
					<NowPlaying nowPlaying={queueState?.data?.nowPlaying}/>
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
						<Box sx={{ display: "flex" }}>
							<UrlPagination
								getPageUrl={getPageUrl}
								totalRows={queueState.data?.totalRows}
							/>
						</Box>
					</> :
						<Typography>No records</Typography>}
				</Loader>
			</Box>
		</>
	);
};
