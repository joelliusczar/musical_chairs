import React, { useEffect, useState, useReducer } from "react";
import { Link, useLocation } from "react-router-dom";
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
	waitingReducer,
	pageableDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import Loader from "../Shared/Loader";
import { DomRoutes } from "../../constants";
import { StationSelect } from "../Shared/StationSelect";
import { urlBuilderFactory } from "../../Helpers/pageable_helpers";
import { UrlPagination } from "../Shared/UrlPagination";
import { formatError } from "../../Helpers/error_formatter";
import { useHasAnyRoles } from "../../Context_Providers/AuthContext";
import { UserRoleDef } from "../../constants";
import { OptionsButton } from "../Shared/OptionsButton";
import { getDownloadAddress } from "../../Helpers/url_helpers";


export const History = () => {

	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const stationNameFromQS = queryObj.get("name") || "";
	const canEditSongs = useHasAnyRoles([UserRoleDef.SONG_EDIT]);
	const canDownloadSongs = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);

	const [currentQueryStr, setCurrentQueryStr] = useState("");

	const [historyState, historyDispatch] =
		useReducer(waitingReducer(), pageableDataInitialState);

	const { callStatus: historyCallStatus } = historyState;

	const getPageUrl = urlBuilderFactory(DomRoutes.history);

	const rowButton = (item, idx) => {
		const rowButtonOptions = [];

		if (canEditSongs) rowButtonOptions.push({
			label: "Edit",
			link: `${DomRoutes.songEdit}?id=${item.id}`,
		});

		if (canDownloadSongs) rowButtonOptions.push({
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
				to={`${DomRoutes.songEdit}?id=${item.id}`}
			>
				View
			</Button>);
	};

	useEffect(() => {
		document.title =
			`Musical Chairs - History${`- ${stationNameFromQS || ""}`}`;
	},[stationNameFromQS]);

	useEffect(() => {
		const fetch = async () => {
			if (currentQueryStr === location.search) return;
			const queryObj = new URLSearchParams(location.search);
			const stationNameFromQS = queryObj.get("name");
			if (!stationNameFromQS) return;

			const page = parseInt(queryObj.get("page") || "1");
			const limit = parseInt(queryObj.get("rows") || "50");
			historyDispatch(dispatches.started());
			try {
				const data = await fetchHistory({
					station: stationNameFromQS,
					params: { page: page - 1, limit: limit } }
				);
				historyDispatch(dispatches.done(data));
				setCurrentQueryStr(location.search);
			}
			catch (err) {
				historyDispatch(dispatches.failed(formatError(err)));
			}

		};
		fetch();
	},[
		historyDispatch,
		fetchHistory,
		location.search,
		currentQueryStr,
		setCurrentQueryStr,
	]);

	return (
		<>
			<h1>History: {stationNameFromQS}</h1>
			<Box m={1}>
				<StationSelect getPageUrl={getPageUrl} />
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
								getPageUrl={getPageUrl}
								totalRows={historyState.data?.totalRows}
							/>
						</Box>
					</>:
						<Typography>No records</Typography>}
				</Loader>
			</Box>
		</>
	);
};
