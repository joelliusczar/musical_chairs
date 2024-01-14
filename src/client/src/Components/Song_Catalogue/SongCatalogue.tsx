import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import {
	fetchSongCatalogue,
	sendSongRequest,
} from "../../API_Calls/stationCalls";
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
import Loader from "../Shared/Loader";
import { DomRoutes } from "../../constants";
import {
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { useSnackbar } from "notistack";
import { UrlBuilder } from "../../Helpers/pageable_helpers";
import { StationRouteSelect } from "../Stations/StationRouteSelect";
import { UrlPagination } from "../Shared/UrlPagination";
import { OptionsButton } from "../Shared/OptionsButton";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { getDownloadAddress } from "../../Helpers/request_helpers";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { StationInfo, StationTableData } from "../../Types/station_types";
import { SongListDisplayItem } from "../../Types/song_info_types";
import { IdValue } from "../../Types/generic_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";

export const SongCatalogue = () => {

	const [catalogueState, catalogueDispatch] = useDataWaitingReducer(
		new RequiredDataStore<StationTableData<SongListDisplayItem>>(
			{
				items: [],
				totalrows: 0,
				stationrules: [],
			}
		)
	);


	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const [selectedStation, setSelectedStation] = useState<StationInfo | null>();
	const location = useLocation();
	const pathVars = useParams();

	const authReset = useCallback(() => {
		catalogueDispatch(dispatches.restart());
	}, [catalogueDispatch]);

	useAuthViewStateChange(authReset);

	const canRequestSongs = useHasAnyRoles([UserRoleDef.STATION_REQUEST]);
	const canRequestSongsForStation = anyConformsToAnyRule(
		catalogueState?.data?.stationrules,
		[UserRoleDef.STATION_REQUEST]
	);
	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadSongs = useHasAnyRoles([UserRoleDef.PATH_DOWNLOAD]);


	const { callStatus: catalogueCallStatus } = catalogueState;
	const { enqueueSnackbar } = useSnackbar();

	const requestSong = async (songId: IdValue) => {
		if (!pathVars.stationkey || !pathVars.ownerkey ) {
			enqueueSnackbar("A key is missing", {variant: "error" });
			return;
		}
		try {
			const requestObj = sendSongRequest({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				songid: songId });
			await requestObj.call();
			enqueueSnackbar("Request has been queued.", { variant: "success"});
		}
		catch (err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	const getPageUrl = new UrlBuilder(DomRoutes.songCatalogue);

	const rowButton = (item: SongListDisplayItem, idx: number) => {
		const rowButtonOptions = [];


		if(canRequestSongs || canRequestSongsForStation) rowButtonOptions.push({
			label: "Request",
			onClick:() => requestSong(item.id),
		});

		const canEditThisSong = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PATH_EDIT]
		);

		if (canEditSongs || canEditThisSong) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit()}?ids=${item.id}`,
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
			`Musical Chairs - Song Catalogue${stationTitle}`;
	},[selectedStation]);

	useEffect(() => {
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = new URLSearchParams(location.search);
		if (!pathVars.stationkey || !pathVars.ownerkey) return;

		const page = parseInt(queryObj.get("page") || "1");
		const limit = parseInt(queryObj.get("rows") || "50");
		const requestObj = fetchSongCatalogue({
			stationkey: pathVars.stationkey,
			ownerkey: pathVars.ownerkey,
			page: page - 1,
			limit: limit,
		}
		);
		const fetch = async () => {
			catalogueDispatch(dispatches.started());
			try {
				const data = await requestObj.call();
				catalogueDispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);
			}
			catch (err) {
				catalogueDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();

		return () => requestObj.abortController.abort();
	},[
		catalogueDispatch,
		pathVars.stationkey,
		pathVars.ownerkey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>Song Catalogue: {selectedStation?.displayname || ""}</h1>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={getPageUrl.getOtherUrl}
					onChange={setStationCallback}
				/>
			</Box>
			<Box m={1}>
				<Loader
					status={catalogueCallStatus}
					error={catalogueState.error}
				>
					{catalogueState?.data?.items?.length > 0 ? <>
						<TableContainer>
							<Table size="small">
								<TableHead>
									<TableRow>
										<TableCell>Song</TableCell>
										<TableCell>Album</TableCell>
										<TableCell>Artist</TableCell>
										<TableCell></TableCell>
									</TableRow>
								</TableHead>
								<TableBody>
									{catalogueState.data.items.map((item, idx) => {
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
								totalRows={catalogueState.data?.totalrows}
							/>
						</Box>
					</>:
						<Typography>No records</Typography>
					}
				</Loader>
			</Box>
		</>
	);
};
