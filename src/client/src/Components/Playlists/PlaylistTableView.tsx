import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { Calls } from "../../API_Calls/playlistCalls";
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
import { UrlBuilder, getSearchParams } from "../../Helpers/pageable_helpers";
import { UrlPagination } from "../Shared/UrlPagination";
import { OptionsButton } from "../Shared/OptionsButton";
import { SearchTextField } from "../Shared/SearchTextFIeld";
import {
	useCurrentUser,
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	PlaylistInfo,
} from "../../Types/playlist_types";
import {
	PageableListDataShape,
} from "../../Types/reducerTypes";



export const PlaylistTableView = () => {

	const location = useLocation();
	const pathVars = useParams();
	const currentUser = useCurrentUser();
	const canEditPlaylist = useHasAnyRoles([UserRoleDef.PLAYLIST_EDIT]);



	const [currentQueryStr, setCurrentQueryStr] = useState("");


	const [tableDataState, tableDataDispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<PlaylistInfo>>({
			items: [],
			totalrows: 0,
		})
	);

	const { callStatus: queueCallStatus } = tableDataState;


	const authReset = useCallback(() => {
		tableDataDispatch(dispatches.restart());
	}, [tableDataDispatch]);

	useAuthViewStateChange(authReset);

	const urlBuilder = new UrlBuilder(DomRoutes.playlistsPage);

	const rowButton = (item: PlaylistInfo, idx?: number) => {
		const rowButtonOptions = [];


		const canEditThisPlaylist = canEditPlaylist &&
			currentUser.id == item.owner.id;

		if (canEditThisPlaylist) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.playlistEdit({
				ownerkey: item.owner.username,
				playlistkey: item.name,
			})}`,
		});

		return (rowButtonOptions.length > 1 ? <OptionsButton
			id={`queue-row-btn-${item.id}-${idx}`}
			options={rowButtonOptions}
		/> :
			<Button
				variant="contained"
				component={Link}
				to={`${DomRoutes.playlistEdit({
					ownerkey: item.owner.username,
					playlistkey: item.name,
				})}`}
			>
				{canEditThisPlaylist ? "Edit" : "View"}
			</Button>);
	};


	useEffect(() => {
		document.title = "Musical Chairs - Playlists";
	},[]);


	useEffect(() => {
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = getSearchParams(location.search);
		const requestObj = Calls.getPage({
			...queryObj,
		});
		const fetch = async () => {
			tableDataDispatch(dispatches.started());
			try {
				const data = await requestObj.call();
				tableDataDispatch(dispatches.done(data));
				setCurrentQueryStr(`${location.pathname}${location.search}`);
			}
			catch (err) {
				tableDataDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
		return () => requestObj.abortController.abort();
	},[
		tableDataDispatch,
		pathVars.stationkey,
		pathVars.ownerkey,
		location.search,
		location.pathname,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>Playlists</h1>
			<Button
				component={Link}
				to={`${DomRoutes.playlistAdd()}`}
			>
				New Playlist
			</Button>
			<Box m={1}>
				<Loader
					status={queueCallStatus}
					error={tableDataState.error}
				>
					<TableContainer>
						<Table size="small">
							<TableHead>
								<TableRow>
									<TableCell>Playlist</TableCell>
									<TableCell></TableCell>
								</TableRow>
								<TableRow>
									<TableCell>
										<SearchTextField
											name="name"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell></TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{tableDataState?.data?.items?.map((item, idx) => {
									return (
										<TableRow key={`playlist_${idx}`}>
											<TableCell>
												{item.name || "{No playlist name}"}
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
					{(tableDataState?.data?.items?.length || 0) === 0 ?
						<Typography>No records</Typography> :
						<></>
					}
					<Box sx={{ display: "flex" }}>
						<UrlPagination
							getPageUrl={urlBuilder.getThisUrl}
							totalRows={tableDataState.data?.totalrows}
						/>
					</Box>
				</Loader>
			</Box>
		</>
	);
};

export default PlaylistTableView;