import React, { useEffect, useState, useReducer } from "react";
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
	waitingReducer,
	pageableDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { useSnackbar } from "notistack";
import { urlBuilderFactory } from "../../Helpers/pageable_helpers";
import { StationRouteSelect } from "../Stations/StationRouteSelect";
import { UrlPagination } from "../Shared/UrlPagination";
import { OptionsButton } from "../Shared/OptionsButton";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext";
import { UserRoleDef } from "../../constants";
import { getDownloadAddress } from "../../Helpers/url_helpers";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";


export const SongCatalogue = () => {

	const [catalogueState, catalogueDispatch] =
		useReducer(waitingReducer(), pageableDataInitialState);


	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const [selectedStation, setSelectedStation] = useState();
	const location = useLocation();
	const pathVars = useParams();

	useAuthViewStateChange(catalogueDispatch);

	const canRequestSongs = useHasAnyRoles([UserRoleDef.STATION_REQUEST]);
	const canRequestSongsForStation = anyConformsToAnyRule(
		catalogueState?.data?.stationRules,
		[UserRoleDef.STATION_REQUEST]
	);
	const canEditSongs = useHasAnyRoles([UserRoleDef.PATH_EDIT]);
	const canDownloadSongs = useHasAnyRoles([UserRoleDef.PATH_DOWNLOAD]);


	const { callStatus: catalogueCallStatus } = catalogueState;
	const { enqueueSnackbar } = useSnackbar();

	const requestSong = async (songId) => {
		try {
			await sendSongRequest({stationKey: pathVars.stationKey, songId });
			enqueueSnackbar("Request has been queued.", { variant: "success"});
		}
		catch (err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	const getPageUrl = urlBuilderFactory(DomRoutes.songCatalogue);

	const rowButton = (item, idx) => {
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
			link: `${DomRoutes.songEdit()}?id=${item.id}`,
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
				{(canEditSongs || canEditThisSong) ? "Edit" : "View"}
			</Button>);
	};

	useEffect(() => {
		const stationTitle = `- ${selectedStation?.displayName || ""}`;
		document.title =
			`Musical Chairs - Song Catalogue${stationTitle}`;
	},[selectedStation]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === `${location.pathname}${location.search}`) return;
			const queryObj = new URLSearchParams(location.search);
			if (!pathVars.stationKey) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			catalogueDispatch(dispatches.started());
			try {
				const data = await fetchSongCatalogue({
					stationKey: pathVars.stationKey,
					ownerKey: pathVars.ownerKey,
					params: { page: page - 1, limit: limit } }
				);
				catalogueDispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);
			}
			catch (err) {
				catalogueDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
	},[
		catalogueDispatch,
		fetchSongCatalogue,
		pathVars.stationKey,
		pathVars.ownerKey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);


	return (
		<>
			<h1>Song Catalogue: {selectedStation?.displayName || ""}</h1>
			<Box m={1}>
				<StationRouteSelect
					getPageUrl={getPageUrl}
					onChange={(s) => setSelectedStation(s)}
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
								getPageUrl={getPageUrl}
								totalRows={catalogueState.data?.totalRows}
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