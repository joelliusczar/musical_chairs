import React, { useEffect, useState, useReducer } from "react";
import { useLocation } from "react-router-dom";
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
	Button,
	Box,
	Typography,
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
import { StationSelect } from "../Shared/StationSelect";
import { UrlPagination } from "../Shared/UrlPagination";


export const SongCatalogue = () => {

	const [catalogueState, catalogueDispatch] =
		useReducer(waitingReducer(), pageableDataInitialState);

	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const stationNameFromQS = queryObj.get("name") || "";

	const { callStatus: catalogueCallStatus } = catalogueState;
	const { enqueueSnackbar } = useSnackbar();

	const requestSong = async (songId) => {
		try {
			await sendSongRequest({station: stationNameFromQS, songId });
			enqueueSnackbar("Request has been queued.", { variant: "success"});
		}
		catch (err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	};

	const getPageUrl = urlBuilderFactory(DomRoutes.songCatalogue);

	useEffect(() => {
		document.title =
			`Musical Chairs - Song Catalogue${`- ${stationNameFromQS || ""}`}`;
	},[stationNameFromQS]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === location.search) return;
			const queryObj = new URLSearchParams(location.search);
			const stationNameFromQS = queryObj.get("name");
			if (!stationNameFromQS) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			catalogueDispatch(dispatches.started());
			try {
				const data = await fetchSongCatalogue({
					station: stationNameFromQS,
					params: { page: page - 1, limit: limit } }
				);
				catalogueDispatch(dispatches.done(data));
				setCurrentQueryStr(location.search);
			}
			catch (err) {
				catalogueDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
	},[
		catalogueDispatch,
		fetchSongCatalogue,
		location.search,
		currentQueryStr,
		setCurrentQueryStr,
	]);


	return (
		<>
			<h1>Song Catalogue: {stationNameFromQS}</h1>
			<Box m={1}>
				<StationSelect getPageUrl={getPageUrl} />
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
										<TableCell>Request</TableCell>
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
													<Button
														color="primary"
														variant="contained"
														onClick={() => requestSong(item.id)}
													>
														Request
													</Button>
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
