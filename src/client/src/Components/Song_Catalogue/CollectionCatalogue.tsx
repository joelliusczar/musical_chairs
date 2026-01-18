import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import {
	Calls,
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
import { DomRoutes, StationTypes, StationRequestTypes } from "../../constants";
import {
	dataDispatches as dispatches,
	useDataWaitingReducer,
} from "../../Reducers/dataWaitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { useSnackbar } from "notistack";
import { UrlBuilder, getSearchParams } from "../../Helpers/pageable_helpers";
import { StationRouteSelect } from "../Stations/StationRouteSelect";
import { UrlPagination } from "../Shared/UrlPagination";
import { OptionsButton } from "../Shared/OptionsButton";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { StationInfo, StationTableData } from "../../Types/station_types";
import { CatalogueItem } from "../../Types/song_info_types";
import { IdValue } from "../../Types/generic_types";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import { SearchTextField } from "../Shared/SearchTextFIeld";



export const CollectionCatalogue = () => {

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

	const canRequest = useHasAnyRoles([UserRoleDef.STATION_REQUEST]);
	const canRequestForStation = anyConformsToAnyRule(
		catalogueState?.data?.stationrules,
		[UserRoleDef.STATION_REQUEST]
	);

	const { callStatus: catalogueCallStatus } = catalogueState;
	const { enqueueSnackbar } = useSnackbar();

	const requestCollection = async (
		collectionId: IdValue,
		requesttypeid: IdValue
	) => {
		if (!pathVars.stationkey || !pathVars.ownerkey ) {
			enqueueSnackbar("A key is missing", {variant: "error" });
			return;
		}
		try {
			const requestObj = Calls.queueRequest({
				stationkey: pathVars.stationkey,
				ownerkey: pathVars.ownerkey,
				itemid: collectionId,
				requesttypeid: requesttypeid,
			});
			await requestObj.call();
			enqueueSnackbar("Request has been queued.", { variant: "success"});
		}
		catch (err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	const getPageUrl = new UrlBuilder(DomRoutes.songCatalogue);

	const rowButton = (item: CatalogueItem, idx: number) => {
		const rowButtonOptions = [];

		const canEditThisAlbum = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.ALBUM_EDIT]
		);

		const canEditThisPlaylist = anyConformsToAnyRule(
			item?.rules,
			[UserRoleDef.PLAYLIST_EDIT]
		);


		if (canEditThisAlbum) {
			if (item.requesttypeid === StationRequestTypes.ALBUM) {
				rowButtonOptions.push({
					label: "Edit",
					link: DomRoutes.album({ id: item.id }),
				});
			}
		}

		if (canEditThisPlaylist) {
			if (item.requesttypeid === StationRequestTypes.PLAYLIST) {
				rowButtonOptions.push({
					label: "Edit",
					link: DomRoutes.playlistEdit(
						{ 
							playlistkey: item.name, 
							ownerkey: item.owner.username,
						}),
				});
			}
		}

		if(canRequest || canRequestForStation) rowButtonOptions.push({
			label: "Request",
			onClick:() => requestCollection(item.id, item.requesttypeid),
		});

		if (rowButtonOptions.length > 1) {
			return <OptionsButton
				id={`queue-row-btn-${idx}`}
				options={rowButtonOptions}
			/>;
		}

		return <Button
			variant="contained"
			component={Link}
			to={
				item.requesttypeid === StationRequestTypes.ALBUM
					? `${DomRoutes.album({ id: item.id })}`
					: `${DomRoutes.playlistEdit(
						{ 
							playlistkey: item.name, 
							ownerkey: item.owner.username,
						})}`
			} 
		>
			{
				(canEditThisAlbum && item.requesttypeid === StationRequestTypes.ALBUM) 
				|| (canEditThisPlaylist 
					&& item.requesttypeid === StationRequestTypes.PLAYLIST)
					? "Edit" : "View"}
		</Button>;
	};

	const setStationCallback = useCallback(
		(s: StationInfo | null) => setSelectedStation(s),
		[setSelectedStation]
	);

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayname || ""}`;
		document.title =
			`Musical Chairs - Album/Playlist Catalogue${stationTitle}`;
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
				Catalogue: {selectedStation?.displayname || ""}
			</h1>
			<h2>
				{catalogueState?.data?.totalrows || ""} albums/playlists 
					on this station.
			</h2>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={getPageUrl.getOtherUrl}
					onChange={setStationCallback}
					stationTypes={[StationTypes.ALBUMS_AND_PLAYLISTS]}
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
										<TableCell>Row #</TableCell>
										<TableCell>Name</TableCell>
										<TableCell>Creator</TableCell>
										<TableCell>Type</TableCell>
										<TableCell></TableCell>
									</TableRow>
									<TableRow>
										<TableCell>
											<SearchTextField
												name="collection"
												getPageUrl={getPageUrl.getThisUrl}
											/>
										</TableCell>
										<TableCell>
											<SearchTextField
												name="creator"
												getPageUrl={getPageUrl.getThisUrl}
											/>
										</TableCell>
										<TableCell>
											<SearchTextField
												name="_blank_"
												disabled
												getPageUrl={getPageUrl.getThisUrl}
											/>
										</TableCell>
										<TableCell></TableCell>
									</TableRow>
								</TableHead>
								<TableBody>
									{catalogueState.data.items.map((item, idx) => {
										return (
											<TableRow key={`song_${idx}`}>
												<TableCell>{idx + 1}</TableCell>
												<TableCell>
													{item.name || "{No name}"}
												</TableCell>
												<TableCell>
													{item.creator || "{No name}"}
												</TableCell>
												<TableCell>
													{item.itemtype || "{No type}"}
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

export default CollectionCatalogue;