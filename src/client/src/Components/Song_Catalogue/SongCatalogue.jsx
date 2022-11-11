import React, { useEffect, useState, useReducer } from "react";
import { useHistory, useParams, useLocation, Link } from "react-router-dom";
import {
	fetchStations,
	fetchSongCatalogue,
	sendSongRequest,
} from "../../API_Calls/stationCalls";
import { MenuItem,
	Select,
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Button,
	Pagination,
	PaginationItem,
	Box,
	TextField,
	Typography,
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import Loader from "../Shared/Loader";
import { DomRoutes } from "../../constants";
import {
	waitingReducer,
	listDataInitialState,
	pageableDataInitialState,
	dispatches,
} from "../Shared/waitingReducer";
import { formatError } from "../../Helpers/error_formatter";
import { useSnackbar } from "notistack";


const useStyles = makeStyles(() => ({
	select: {
		width: 150,
	},
}));

export const SongCatalogue = () => {

	const [stationsState, stationsDispatch] =
		useReducer(waitingReducer(), listDataInitialState);
	const [catalogueState, catalogueDispatch] =
		useReducer(waitingReducer(), pageableDataInitialState);

	const [currentQueryStr, setCurrentQueryStr] = useState("");
	const { station: stationParam } = useParams();
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const page = parseInt(queryObj.get("page") || "1");
	const stationNameFromQS = queryObj.get("name") || "";
	const urlHistory = useHistory();
	const classes = useStyles();

	const { callStatus: stationsCallStatus } = stationsState;
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

	const getPageUrl = (params) => {
		const queryObj = new URLSearchParams(location.search);
		if(params.page) {
			queryObj.set("page", params.page);
		}
		if(params.rows) {
			queryObj.set("rows", params.rows);
		}
		if(params.id) {
			queryObj.set("id", params.id);
		}
		if(params.name) {
			queryObj.set("name", params.name);
		}
		else if (params.name === "") {
			queryObj.delete("name");
		}
		const queryStr = `?${queryObj.toString()}`;
		return `${DomRoutes.songCatalogue}${queryStr}`;
	};

	const getPageCount = () => {
		const rows = parseInt(queryObj.get("rows") || "1");
		const totalRows = catalogueState.data.totalRows;
		if(rows < 1) {
			return 0;
		}
		return Math.floor(totalRows / rows);
	};

	const getRowsCount = () => {
		return parseInt(queryObj.get("rows") || "50");
	};

	useEffect(() => {
		const fetch = async () => {
			if (!stationsCallStatus) {
				stationsDispatch(dispatches.started());
				try {
					const data = await fetchStations();
					stationsDispatch(dispatches.done(data));
				}
				catch(err) {
					stationsDispatch(dispatches.failed(formatError(err)));
				}

			}
		};
		fetch();
	}, [stationsCallStatus, stationsDispatch]);

	useEffect(() => {
		document.title =
			`Musical Chairs - Song Catalogue${`- ${stationParam || ""}`}`;
	},[stationParam]);

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
			<h1>Song Catalogue: {stationParam}</h1>
			{stationsState?.data?.items?.length > 0 && (
				<Box m={1}>
					<TextField
						select
						className={classes.select}
						label="Stations"
						onChange={(e) => {
							urlHistory.replace(getPageUrl({ name: e.target.value }));
						}}
						value={stationNameFromQS?.toLowerCase() || ""}
					>
						<MenuItem key="empty_station" value={""}>
								Select a Station
						</MenuItem>
						{stationsState.data.items.map((s) => {
							return (
								<MenuItem key={s.name} value={s.name?.toLowerCase()}>
									{s.displayName}
								</MenuItem>
							);
						})}
					</TextField>
				</Box>
			)}
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
							<Select
								displayEmpty
								defaultValue={50}
								label="Row Count"
								onChange={(e) => {
									urlHistory.replace(
										getPageUrl({ rows: e.target.value, page: 1 })
									);
								}}
								renderValue={(v) => v || "Select Row Count"}
								value={getRowsCount()}
							>
								{[10, 50, 100, 1000].map((size) => {
									return (<MenuItem key={`size_${size}`} value={size}>
										{size}
									</MenuItem>);
								})}
							</Select>
							<Pagination
								count={getPageCount()}
								page={page}
								renderItem={item => {
									return (<PaginationItem
										component={Link}
										to={getPageUrl({ page: item.page })}
										{...item} />);
								} }
								sx={{}} />
						</Box>
					</>:
						<Typography>No records</Typography>
					}
				</Loader>
			</Box>
		</>
	);
};
