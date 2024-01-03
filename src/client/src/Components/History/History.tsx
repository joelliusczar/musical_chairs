import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { fetchHistory } from "../../API_Calls/stationCalls";
import {
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Box,
	Typography,
	Button,
} from "@mui/material";
import {
	dispatches,
} from "../../Reducers/waitingReducer";
import { useDataWaitingReducer } from "../../Reducers/dataWaitingReducer";
import Loader from "../Shared/Loader";
import { DomRoutes } from "../../constants";
import { StationRouteSelect } from "../Stations/StationRouteSelect";
import { UrlBuilder } from "../../Helpers/pageable_helpers";
import { UrlPagination } from "../Shared/UrlPagination";
import { formatError } from "../../Helpers/error_formatter";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext";
import { UserRoleDef } from "../../constants";
import { OptionsButton } from "../Shared/OptionsButton";
import { getDownloadAddress } from "../../Helpers/request_helpers";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { StationInfo } from "../../Types/station_types";
import {
	PageableListDataShape,
} from "../../Reducers/types/reducerTypes";
import { SongListDisplayItem } from "../../Types/song_info_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";


export const History = () => {

	const location = useLocation();
	const pathVars = useParams();
	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadAnySong = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);

	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const [selectedStation, setSelectedStation] = useState<StationInfo | null>();

	const [historyState, historyDispatch] =
		useDataWaitingReducer(
			new RequiredDataStore<PageableListDataShape<SongListDisplayItem>>(
				{
					items: [],
					totalrows: 0,
				}
			)
		);

	useAuthViewStateChange(historyDispatch);

	const { callStatus: historyCallStatus } = historyState;

	const getPageUrl = new UrlBuilder(DomRoutes.history);

	const rowButton = (item: SongListDisplayItem, idx: number) => {
		const rowButtonOptions = [];
		const canEditThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_EDIT]
		);
		const canDownloadThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_DOWNLOAD]
		);
		if (canEditSongs || canEditThisSong) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit()}?ids=${item.id}`,
		});

		if (canDownloadAnySong || canDownloadThisSong) rowButtonOptions.push({
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
				to={`${DomRoutes.songEdit()}?ids=${item.id}`}
			>
				{(canEditSongs || canEditThisSong) ? "Edit" : "View"}
			</Button>);
	};

	const setStationCallback = useCallback(
		(s: StationInfo | null) => setSelectedStation(s),
		[setSelectedStation]
	);

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayname || ""}`;
		document.title =
			`Musical Chairs - History${stationTitle}`;
	},[selectedStation]);

	useEffect(() => {
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = new URLSearchParams(location.search);
		if (!pathVars.stationkey || !pathVars.ownerkey) return;

		const page = parseInt(queryObj.get("page") || "1");
		const limit = parseInt(queryObj.get("rows") || "50");
		const requestObj = fetchHistory({
			stationkey: pathVars.stationkey,
			ownerkey: pathVars.ownerkey,
			page: page - 1,
			limit: limit,
		});
		const fetch = async () => {
			historyDispatch(dispatches.started());
			try {
				const data = await requestObj.call();
				historyDispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);

			}
			catch (err) {
				historyDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
		return () => requestObj.abortController.abort();
	},[
		historyDispatch,
		pathVars.stationkey,
		pathVars.ownerkey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>History: {selectedStation?.displayname || ""}</h1>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={getPageUrl.getOtherUrl}
					onChange={setStationCallback}
				/>
			</Box>
			<Box m={1}>
				<Loader
					status={historyCallStatus}
					error={historyState.error}
				>
					{historyState?.data?.items?.length > 0 ? <>
						<TableContainer>
							<Table size="small">
								<TableHead>
									<TableRow>
										<TableCell>Song</TableCell>
										<TableCell>Album</TableCell>
										<TableCell>Artist</TableCell>
										<TableCell>Last Played</TableCell>
										<TableCell></TableCell>
									</TableRow>
								</TableHead>
								<TableBody>
									{historyState.data?.items.map((item, idx) => {
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
								getPageUrl={getPageUrl.getThisUrl}
								totalRows={historyState.data?.totalrows}
							/>
						</Box>
					</>:
						<Typography>No records</Typography>}
				</Loader>
			</Box>
		</>
	);
};
