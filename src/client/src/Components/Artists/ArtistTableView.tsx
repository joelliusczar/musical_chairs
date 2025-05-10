import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { getPage } from "../../API_Calls/artistCalls";
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
import { UrlPagination } from "../Shared/UrlPagination";
import { OptionsButton } from "../Shared/OptionsButton";
import {
	useCurrentUser,
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	ArtistInfo,
} from "../../Types/song_info_types";
import {
	PageableListDataShape,
} from "../../Types/reducerTypes";



export const ArtistTableView = () => {

	const location = useLocation();
	const pathVars = useParams();
	const canEditArtists = useHasAnyRoles([UserRoleDef.ARTIST_EDIT]);
	const currentUser = useCurrentUser();


	const [currentQueryStr, setCurrentQueryStr] = useState("");


	const [tableDataState, tableDataDispatch] = useDataWaitingReducer(
		new RequiredDataStore<PageableListDataShape<ArtistInfo>>({
			items: [],
			totalrows: 0,
		})
	);

	const { callStatus } = tableDataState;


	const authReset = useCallback(() => {
		tableDataDispatch(dispatches.restart());
	}, [tableDataDispatch]);

	useAuthViewStateChange(authReset);

	const urlBuilder = new UrlBuilder(DomRoutes.queue);

	const rowButton = (item: ArtistInfo, idx?: number) => {
		const rowButtonOptions = [];


		const canEditThisArtist = canEditArtists && currentUser.id == item.owner.id;
	

		if (canEditThisArtist) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.artist({ id: item.id})}`,
		});

		return (rowButtonOptions.length > 1 ? <OptionsButton
			id={`queue-row-btn-${item.id}-${idx}`}
			options={rowButtonOptions}
		/> :
			<Button
				variant="contained"
				component={Link}
				to={`${DomRoutes.artist({ id: item.id})}`}
			>
				{canEditThisArtist ? "Edit" : "View"}
			</Button>);
	};


	useEffect(() => {
		document.title = "Musical Chairs - Artists";
	},[]);


	useEffect(() => {
		if (currentQueryStr === `${location.pathname}${location.search}`) return;
		const queryObj = new URLSearchParams(location.search);

		const page = parseInt(queryObj.get("page") || "1");
		const limit = parseInt(queryObj.get("rows") || "50");
		const requestObj = getPage({
			page: page,
			limit: limit,
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
			<h1>Artists</h1>
			<Box m={1}>
				<Loader
					status={callStatus}
					error={tableDataState.error}
				>
					{tableDataState?.data?.items?.length > 0 ? <>
						<TableContainer>
							<Table size="small">
								<TableHead>
									<TableRow>
										<TableCell>Artist</TableCell>
										<TableCell></TableCell>
									</TableRow>
								</TableHead>
								<TableBody>
									{tableDataState.data?.items?.map((item, idx) => {
										return (
											<TableRow key={`artist_${idx}`}>
												<TableCell>
													{item.name || "{No artist name}"}
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
						<Box sx={{ display: "flex" }}>
							<UrlPagination
								getPageUrl={urlBuilder.getThisUrl}
								totalRows={tableDataState.data?.totalrows}
							/>
						</Box>
					</> :
						<Typography>No records</Typography>}
				</Loader>
			</Box>
		</>
	);
};