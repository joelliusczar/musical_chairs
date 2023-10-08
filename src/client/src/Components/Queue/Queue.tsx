import React, { useEffect, useState } from "react";
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
	dispatches,
} from "../../Reducers/waitingReducer";
import { useDataWaitingReducer } from "../../Reducers/dataWaitingReducer";
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
} from "../../Context_Providers/AuthContext";
import { UserRoleDef } from "../../constants";
import { getDownloadAddress } from "../../Helpers/url_helpers";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import {
	SongListDisplayItem,
	InitialQueueState,
} from "../../Types/song_info_types";
import { StationInfo } from "../../Types/station_types";



export const Queue = () => {

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

	useAuthViewStateChange(queueDispatch);

	const urlBuilder = new UrlBuilder(DomRoutes.queue);

	const rowButton = (item: SongListDisplayItem, idx: number) => {
		const rowButtonOptions = [];

		const canEditThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_EDIT]
		);

		if (canEditSongs || canEditThisSong) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit()}?ids=${item.id}`,
		});
		if (canSkipSongs || canSkipSongsForStation) rowButtonOptions.push({
			label: "Skip",
			onClick:() => handleRemoveSongFromQueue(item),
		});

		const canDownloadThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_DOWNLOAD]
		);

		if (canDownloadSongs || canDownloadThisSong) rowButtonOptions.push({
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
			const data = await removeSongFromQueue({
				ownerkey: pathVars.ownerkey,
				stationkey: pathVars.stationkey,
				songid: item?.id,
				queuedtimestamp: item?.queuedtimestamp,
			});
			queueDispatch(dispatches.done(data));
			enqueueSnackbar("Song has been removed from queue");
		}
		catch(err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayname || ""}`;
		document.title = `Musical Chairs - Queue${stationTitle}`;
	},[selectedStation]);


	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			if (!pathVars.stationkey || !pathVars.ownerkey) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			queueDispatch(dispatches.started());
			try {
				const data = await fetchQueue({
					stationkey: pathVars.stationkey,
					ownerkey: pathVars.ownerkey,
					page: page - 1,
					limit: limit,
				});
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
					onChange={(s) => setSelectedStation(s)}
				/>
			</Box>
			<Box m={1}>
				<Loader
					status={queueCallStatus}
					error={queueState.error}
				>
					<Typography>Now Playing</Typography>
					<NowPlaying nowPlaying={queueState?.data?.nowplaying}/>
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