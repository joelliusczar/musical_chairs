import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { Calls } from "../../API_Calls/stationCalls";
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
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { UrlBuilder } from "../../Helpers/pageable_helpers";
import { StationRouteSelect } from "../Stations/StationRouteSelect";
import { UrlPagination } from "../Shared/UrlPagination";
import { NowPlaying } from "../Shared/NowPlaying";
import { useSnackbar } from "notistack";
import { OptionsButton } from "../Shared/OptionsButton";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import {
	SongListDisplayItem,
	InitialQueueState,
} from "../../Types/song_info_types";
import { StationInfo } from "../../Types/station_types";
import { openSongInTab } from "../../API_Calls/songInfoCalls";



const Queue = () => {

	const location = useLocation();
	const pathVars = useParams();
	const { enqueueSnackbar } = useSnackbar();
	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canSkipSongs = useHasAnyRoles([UserRoleDef.STATION_SKIP]);
	const canDownloadSongs = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);


	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const [selectedStation, setSelectedStation] = useState<StationInfo | null>();


	const [queueState, queueDispatch] = useDataWaitingReducer(
		new InitialQueueState()
	);

	const { callStatus: queueCallStatus } = queueState;
	const canSkipSongsForStation = anyConformsToAnyRule(
		queueState?.data?.stationrules,
		[UserRoleDef.STATION_SKIP]
	);

	const authReset = useCallback(() => {
		queueDispatch(dispatches.restart());
	}, [queueDispatch]);

	useAuthViewStateChange(authReset);

	const urlBuilder = new UrlBuilder(DomRoutes.queue);

	const rowButton = (item: SongListDisplayItem, idx?: number) => {
		const rowButtonOptions = [];
		const isSongSkippable = typeof(idx) === "number";

		const canEditThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_EDIT]
		);

		if (canEditSongs || canEditThisSong) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit()}?ids=${item.id}`,
		});
		if ((canSkipSongs || canSkipSongsForStation) && isSongSkippable) {
			rowButtonOptions.push({
				label: "Skip",
				onClick:() => handleRemoveSongFromQueue(item),
			});
		}

		const canDownloadThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_DOWNLOAD]
		);

		if (canDownloadSongs || canDownloadThisSong) rowButtonOptions.push({
			label: "Download",
			onClick: () => openSongInTab(item.id),
		});

		return (rowButtonOptions.length > 1 ? <OptionsButton
			id={`queue-row-btn-${item.id}-${idx}`}
			options={rowButtonOptions}
		/> :
			<Button
				variant="contained"
				component={Link}
				to={`${DomRoutes.songEdit()}?id=${item.id}`}
			>
				View
			</Button>);
	};

	const handleRemoveSongFromQueue = async (item: SongListDisplayItem) => {
		try {
			if (!pathVars.ownerkey || !pathVars.stationkey) {
				enqueueSnackbar("Station or user missing", {variant: "error" });
				return;
			}
			const requestObj = Calls.removeSongFromQueue({
				ownerkey: pathVars.ownerkey,
				stationkey: pathVars.stationkey,
				songid: item?.id,
				queuedtimestamp: item?.queuedtimestamp,
			});
			const data = await requestObj.call();
			queueDispatch(dispatches.done(data));
			enqueueSnackbar("Song has been removed from queue");
		}
		catch(err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	const setStationCallback = useCallback(
		(s: StationInfo | null) => setSelectedStation(s),
		[setSelectedStation]
	);

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayname || ""}`;
		document.title = `Musical Chairs - Queue${stationTitle}`;
	},[selectedStation]);


	useEffect(() => {
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = new URLSearchParams(location.search);
		if (!pathVars.stationkey || !pathVars.ownerkey) return;

		const page = parseInt(queryObj.get("page") || "1");
		const limit = parseInt(queryObj.get("rows") || "50");
		const requestObj = Calls.getQueue({
			stationkey: pathVars.stationkey,
			ownerkey: pathVars.ownerkey,
			page: page,
			limit: limit,
		});
		const fetch = async () => {
			queueDispatch(dispatches.started());
			try {
				const data = await requestObj.call();
				queueDispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);
			}
			catch (err) {
				queueDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
		return () => requestObj.abortController.abort();
	},[
		queueDispatch,
		pathVars.stationkey,
		pathVars.ownerkey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>Queue: {selectedStation?.displayname || ""}</h1>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={urlBuilder.getOtherUrl}
					onChange={setStationCallback}
				/>
			</Box>
			<Box m={1}>
				<Loader
					status={queueCallStatus}
					error={queueState.error}
				>
					<Typography>
						Now Playing
					</Typography>
					<NowPlaying nowPlaying={queueState?.data?.nowplaying}/>
					<>
						{!!queueState?.data?.nowplaying &&
							rowButton(queueState?.data?.nowplaying)
						}
					</>
					{queueState?.data?.items?.length > 0 ? <>
						<TableContainer>
							<Table size="small">
								<TableHead>
									<TableRow>
										<TableCell>Song</TableCell>
										<TableCell>Album</TableCell>
										<TableCell>Artist</TableCell>
										<TableCell>Added</TableCell>
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
												<TableCell>
													{new Date(
														item.queuedtimestamp * 1000
													).toLocaleString()}
												</TableCell>
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
								getPageUrl={urlBuilder.getThisUrl}
								totalRows={queueState.data?.totalrows}
							/>
						</Box>
					</> :
						<Typography>No records</Typography>}
				</Loader>
			</Box>
		</>
	);
};

export default Queue;