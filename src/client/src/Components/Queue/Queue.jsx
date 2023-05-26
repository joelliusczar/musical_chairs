import React, { useEffect, useState, useReducer } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { fetchQueue, removeSongFromQueue } from "../../API_Calls/stationCalls";
import {
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Typography,
	Box,
	Button,
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
import { useSnackbar } from "notistack";
import { OptionsButton } from "../Shared/OptionsButton";
import { useHasAnyRoles } from "../../Context_Providers/AuthContext";
import { UserRoleDef } from "../../constants";
import { getDownloadAddress } from "../../Helpers/url_helpers";

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


export const Queue = () => {

	const location = useLocation();
	const pathVars = useParams();
	const queryObj = new URLSearchParams(location.search);
	const { enqueueSnackbar } = useSnackbar();
	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canSkipSongs = useHasAnyRoles([UserRoleDef.STATION_SKIP]);
	const canDownloadSongs = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);

	const [currentQueryStr, setCurrentQueryStr] = useState("");

	const [queueState, queueDispatch] =
		useReducer(waitingReducer(),
			queueInitialState
		);

	const { callStatus: queueCallStatus } = queueState;

	const getPageUrl = urlBuilderFactory(DomRoutes.queue);

	const rowButton = (item, idx) => {
		const rowButtonOptions = [];

		if (canEditSongs) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit}?id=${item.id}`,
		});

		if (canSkipSongs) rowButtonOptions.push({
			label: "Skip",
			onClick:() => handleRemoveSongFromQueue(item),
		});

		if (canDownloadSongs) rowButtonOptions.push({
			label: "Download",
			href: getDownloadAddress(item.id),
		});

		return (rowButtonOptions.length > 1 ? <OptionsButton
			id={`queue-row-btn-${idx}`}
			options={rowButtonOptions}
		/> :
			<Button
				variant="contained"
				component={Link}
				to={`${DomRoutes.songEdit}?id=${item.id}`}
			>
				View
			</Button>);
	};

	const handleRemoveSongFromQueue = async (item) => {
		try {
			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			const data = await removeSongFromQueue({
				stationName: pathVars.stationKey,
				songId: item?.id,
				queuedTimestamp: item?.queuedTimestamp,
				page: page - 1,
				limit: limit,
			});
			queueDispatch(dispatches.done(data));
			enqueueSnackbar("Song has been removed from queue");
		}
		catch(err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	useEffect(() => {
		const stationTitle = `- ${pathVars.stationKey || ""}`;
		document.title = `Musical Chairs - Queue${stationTitle}`;
	},[pathVars.stationKey]);


	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			if (!pathVars.stationKey) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			queueDispatch(dispatches.started());
			try {
				const data = await fetchQueue({
					stationKey: pathVars.stationKey,
					ownerKey: pathVars.ownerKey,
					params: { page: page - 1, limit: limit } }
				);
				queueDispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);
			}
			catch (err) {
				queueDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
	},[
		queueDispatch,
		fetchQueue,
		pathVars.stationKey,
		pathVars.ownerKey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>Queue: {pathVars.stationKey}</h1>
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
										<TableCell></TableCell>
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
												<TableCell>
													{rowButton(item, idx)}
												</TableCell>
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
