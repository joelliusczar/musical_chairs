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
	Box,
	Typography,
	Button,
} from "@mui/material";
import Loader from "../Shared/Loader";
import { DomRoutes, StationTypes } from "../../constants";
import {
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { useSnackbar } from "notistack";
import { UrlBuilder, getSearchParams } from "../../Helpers/pageable_helpers";
import { StationRouteSelect } from "../Stations/StationRouteSelect";
import { OptionsButton, OrderByField, UrlPagination } from "../Shared";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { StationInfo, StationTableData } from "../../Types/station_types";
import { CatalogueItem } from "../../Types/song_info_types";
import { Token } from "../../Types/generic_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import { SearchTextField } from "../Shared/SearchTextFIeld";
import { openSongInTab } from "../../API_Calls/songInfoCalls";



export const SongCatalogue = () => {

	const [catalogueState, catalogueDispatch] = useDataWaitingReducer(
		new RequiredDataStore<StationTableData<CatalogueItem>>(
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

	const requestSong = async (songId: Token) => {
		if (!pathVars.stationkey || !pathVars.ownerkey ) {
			enqueueSnackbar("A key is missing", {variant: "error" });
			return;
		}
		try {
			const requestObj = Calls.queueRequest({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				itemid: songId });
			await requestObj.call();
			enqueueSnackbar("Request has been queued.", { variant: "success"});
		}
		catch (err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	const urlBuilder = new UrlBuilder(DomRoutes.songCatalogue);


	const rowButton = (item: CatalogueItem, idx: number) => {
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
			onClick: () => openSongInTab(item.id),
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
		if (!pathVars.stationkey || !pathVars.ownerkey) return;
		const queryObj = getSearchParams(location.search);
		const requestObj = Calls.getCatalogue({
			stationkey: pathVars.stationkey,
			ownerkey: pathVars.ownerkey,
			...queryObj,
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
			<h1>
				Song Catalogue: {selectedStation?.displayname || ""}
			</h1>
			<h2>
				{catalogueState?.data?.totalrows || ""} songs on this station.
			</h2>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={urlBuilder.getOtherUrl}
					onChange={setStationCallback}
					stationTypes={[StationTypes.SONGS_ONLY]}
				/>
			</Box>
			<Box m={1}>
				<Loader
					status={catalogueCallStatus}
					error={catalogueState.error}
				>
					<TableContainer>
						<Table size="small">
							<TableHead>
								<TableRow>
									<TableCell>
										Row #
									</TableCell>
									<OrderByField 
										label="Song"
										name="name"
										getPageUrl={urlBuilder.getThisUrl}
									/>
									<OrderByField 
										label="Album"
										name="parentname"
										getPageUrl={urlBuilder.getThisUrl}
									/>
									<OrderByField 
										label="Artist"
										name="creator"
										getPageUrl={urlBuilder.getThisUrl}
									/>
									<OrderByField 
										label="Played Count"
										name="playedcount"
										getPageUrl={urlBuilder.getThisUrl}
									/>
									<TableCell></TableCell>
								</TableRow>
								<TableRow>
									<TableCell></TableCell>
									<TableCell>
										<SearchTextField
											name="name"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell>
										<SearchTextField
											name="parentname"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell>
										<SearchTextField
											name="creator"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell></TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{catalogueState?.data?.items?.map((item, idx) => {
									return (
										<TableRow key={`song_${idx}`}>
											<TableCell>
												{idx + 1}
											</TableCell>
											<TableCell>
												{item.name || "{No song name}"}
											</TableCell>
											<TableCell>
												{item.parentname || "{No album name}"}
											</TableCell>
											<TableCell>
												{item.creator || "{No artist name}"}
											</TableCell>
											<TableCell>
												{item.playedcount || 0}
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
					{(catalogueState?.data?.items?.length || 0) === 0 ?
						<Typography>No records</Typography> :
						<></>
					}
					<Box sx={{ display: "flex" }}>
						<UrlPagination
							getPageUrl={urlBuilder.getThisUrl}
							totalRows={catalogueState.data?.totalrows}
						/>
					</Box>
				</Loader>
			</Box>
		</>
	);
};

export default SongCatalogue;