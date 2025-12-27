import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { Calls } from "../../API_Calls/albumCalls";
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
import { useAlbumData } from "../../Context_Providers/AppContext/AppContext";
import { UserRoleDef } from "../../constants";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	AlbumInfo,
} from "../../Types/song_info_types";
import {
	PageableListDataShape,
} from "../../Types/reducerTypes";



export const AlbumTableView = () => {

	const location = useLocation();
	const pathVars = useParams();
	const currentUser = useCurrentUser();
	const canEditAlbums = useHasAnyRoles([UserRoleDef.ALBUM_EDIT]);



	const [currentQueryStr, setCurrentQueryStr] = useState("");


	const [tableDataState, tableDataDispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<AlbumInfo>>({
			items: [],
			totalrows: 0,
		})
	);

	const { callStatus: queueCallStatus } = tableDataState;

	const { songCounts } = useAlbumData();


	const authReset = useCallback(() => {
		tableDataDispatch(dispatches.restart());
	}, [tableDataDispatch]);

	useAuthViewStateChange(authReset);

	const urlBuilder = new UrlBuilder(DomRoutes.albumPage);

	const rowButton = (item: AlbumInfo, idx?: number) => {
		const rowButtonOptions = [];


		const canEditThisAlbum = canEditAlbums && currentUser.id == item.owner.id;

		if (canEditThisAlbum) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.album({ id: item.id})}`,
		});

		return (rowButtonOptions.length > 1 ? <OptionsButton
			id={`queue-row-btn-${item.id}-${idx}`}
			options={rowButtonOptions}
		/> :
			<Button
				variant="contained"
				component={Link}
				to={`${DomRoutes.album({ id: item.id})}`}
			>
				{canEditThisAlbum ? "Edit" : "View"}
			</Button>);
	};


	useEffect(() => {
		document.title = "Musical Chairs - Albums";
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
			<h1>Albums</h1>
			<Box m={1}>
				<Loader
					status={queueCallStatus}
					error={tableDataState.error}
				>
					<TableContainer>
						<Table size="small">
							<TableHead>
								<TableRow>
									<TableCell>Album</TableCell>
									<TableCell>Version</TableCell>
									<TableCell>Artist</TableCell>
									<TableCell></TableCell>
								</TableRow>
								<TableRow>
									<TableCell>
										<SearchTextField
											name="name"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell>
										<SearchTextField
											name="versionnote"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell>
										<SearchTextField
											name="artist"
											getPageUrl={urlBuilder.getThisUrl}
										/>
									</TableCell>
									<TableCell></TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{tableDataState?.data?.items?.map((item, idx) => {
									return (
										<TableRow key={`album_${idx}`}>
											<TableCell 
												style={!(item.id in songCounts) 
													? { color: "gray"} 
													: {}}
											>
												{item.name || "{No album name}"}
											</TableCell>
											<TableCell>
												{item.versionnote || ""}
											</TableCell>
											<TableCell>
												{item.albumartist?.name}
											</TableCell>
											<TableCell>
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

export default AlbumTableView;