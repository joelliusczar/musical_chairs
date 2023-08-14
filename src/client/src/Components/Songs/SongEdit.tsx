import React, { useReducer, useEffect, useMemo } from "react";
import {
	Box,
	Typography,
	Button,
	Checkbox,
} from "@mui/material";
import * as Yup from "yup";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { FormTextField } from "../Shared/FormTextField";
import {
	useArtistData,
	useAlbumData,
	useStationData,
	useIdMapper,
} from "../../Context_Providers/AppContextProvider";
import Loader from "../Shared/Loader";
import { ArtistNewModalOpener } from "../Artists/ArtistEdit";
import { AlbumNewModalOpener } from "../Albums/AlbumEdit";
import { StationNewModalOpener } from "../Stations/StationEdit";
import { useLocation } from "react-router-dom";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Shared/waitingReducer";
import { useSnackbar } from "notistack";
import {
	fetchSongForEdit,
	saveSongEdits,
	fetchSongsForMultiEdit,
	saveSongsEditsMulti,
} from "../../API_Calls/songInfoCalls";
import { formatError } from "../../Helpers/error_formatter";
import {
	useHasAnyRoles,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext";
import { UserRoleDef } from "../../constants";
import { getDownloadAddress } from "../../Helpers/url_helpers";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import {
	useCombinedContextAndFormItems,
} from "../../Helpers/array_helpers";
import { AlbumSelect } from "../Albums/AlbumSelect";
import { ArtistSelect } from "../Artists/ArtistSelect";
import { StationSelect } from "../Stations/StationSelect";


const inputField = {
	margin: 2,
};


const TouchTypes = {
	set: "set",
	unset: "unset",
	edited: "edited",
};

const createTouchedObject = (touchedArr) => {
	const result = {};
	if (!touchedArr) return result;
	for (const name of touchedArr) {
		result[name] = TouchTypes.set;
	}
	return result;
};

const touchedObjectToArr = (touchedObj) => {
	const result = [];
	if (!touchedObj) return result;
	for (const key in touchedObj) {
		const value = touchedObj[key];
		if(value == TouchTypes.set || TouchTypes.edited) {
			result.push(key);
		}
	}
	return result;
};


const schema = Yup.object().shape({
	"primaryArtist": Yup.object().nullable().test(
		"primaryArtist",
		"Primary Artist is already listed.",
		(value, testContext) => {
			if (testContext.parent.artists?.some(a => a?.id === value?.id)) {
				return false;
			}
			return true;
		}
	),
	"artists": Yup.array().nullable().test(
		"artists",
		"",
		(value, testContext) => {
			if (!value) return true;
			const found = {};
			for (const artist of value) {
				if (artist?.id === testContext.parent.primaryArtist?.id) {
					return testContext.createError({
						message: `Artist ${artist.name} has already been added ` +
						"as primary artist",
					});
				}
				if (found[artist?.id]) {
					return testContext.createError({
						message: `Artist ${artist.name} has already been added`,
					});
				}
				if (artist?.id) {
					found[artist.id] = true;
				}
			}
			return true;
		}
	),
});

export const SongEdit = () => {

	const { enqueueSnackbar } = useSnackbar();
	const [state, dispatch] = useReducer(waitingReducer(), initialState);
	const { callStatus } = state;
	const location = useLocation();
	const canDownloadSongs = useHasAnyRoles([UserRoleDef.SONG_DOWNLOAD]);

	const ids = useMemo(() => {
		const queryObj = new URLSearchParams(location.search);
		return queryObj.getAll("ids").map(id => parseInt(id));
	},[location.search]);

	const {
		items: contextArtists,
		callStatus: artistCallStatus,
		error: artistError,
		add: addArtist,
	} = useArtistData();

	const {
		items: contextAlbums,
		callStatus: albumCallStatus,
		error: albumError,
		add: addAlbum,
	} = useAlbumData();

	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		add: addStation,
	} = useStationData();

	const formMethods = useForm({
		defaultValues: {
			name: "",
			artists: [],
			primaryArtist: {
				id: 0,
				name: "",
			},
			album: {
				id: 0,
				name: "",
			},
			stations: [],
			genre: "",
		},
		resolver: yupResolver(schema),
	});
	const {
		handleSubmit,
		reset,
		watch,
		setValue,
		formState,
	} = formMethods;

	const songRules = watch("rules");
	const canEditSongs = anyConformsToAnyRule(
		songRules, [UserRoleDef.PATH_EDIT]
	);
	const multiSongTouchedField = watch("touched");

	const handleMutliSongTouchedCheck = (name) => {
		const updTouched = {...multiSongTouchedField};
		const value = multiSongTouchedField[name];
		if (value === TouchTypes.edited || value === TouchTypes.set) {
			updTouched[name] = TouchTypes.unset;
		}
		else {
			updTouched[name] = TouchTypes.set;
		}
		setValue("touched", updTouched);
	};

	const isMultSongTouchedChecked = (name) => {
		if (!multiSongTouchedField) return false;
		const value = multiSongTouchedField[name];
		if (value === TouchTypes.edited || value === TouchTypes.set) return true;
		return false;
	};

	// eslint-disable-next-line react/prop-types
	const TouchedCheckbox = ({ name }) => {
		return <Checkbox
			name={name}
			onChange={() => handleMutliSongTouchedCheck(name)}
			checked={isMultSongTouchedChecked(name)}
			disabled={!canEditSongs}
		/>;
	};

	const callSubmit = handleSubmit(async values => {
		try {
			values.touched = touchedObjectToArr(values.touched);
			const data = ids.length < 2 ?
				await saveSongEdits({ id: ids[0], data: values }) :
				await saveSongsEditsMulti({ ids, data: values });
			reset(data);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	});

	useAuthViewStateChange(dispatch);

	useEffect(() => {
		const fetch = async () => {
			try {
				if(ids.length == 1) {
					if(!callStatus) {
						dispatch(dispatches.started());
						const data = await fetchSongForEdit({
							id: ids[0],
						});
						reset(data);
						dispatch(dispatches.done());
					}
				}
				else if(ids.length > 1) {
					if(!callStatus) {
						dispatch(dispatches.started());
						const data = await fetchSongsForMultiEdit({ ids });
						data.touched = createTouchedObject(data.touched);
						reset(data);
						dispatch(dispatches.done());
					}
				}
				else {
					dispatch(dispatches.failed("No song selected"));
				}
			}
			catch(err) {
				dispatch(dispatches.failed(formatError(err)));
			}
		};

		fetch();
	}, [dispatch, callStatus, ids ]);

	useEffect(() => {
		if (ids?.length < 2) return;
		const multiSongTouchedField = watch("touched");
		if(!multiSongTouchedField) return;
		const updTouched = {...multiSongTouchedField};
		let added = false;
		for(const key in formState.touchedFields) {
			const value = updTouched[key];
			if(!value) {
				updTouched[key] = TouchTypes.edited;
				added = true;
			}
		}
		if (added) {
			setValue("touched", updTouched);
		}

	},[formState, setValue, watch, ids]);

	const songFilePath = watch("path");
	const formArtists = watch("artists");
	const primaryArtist = watch("primaryArtist");
	const formAllArtists = useMemo(() =>
		primaryArtist ? [...formArtists, primaryArtist] : formArtists,
	[formArtists, primaryArtist]);
	const artists = useCombinedContextAndFormItems(
		contextArtists,
		formAllArtists
	);

	const album = watch("album");
	const albumAsArray = useMemo(() => album ? [album] : [],[album]);

	const albums = useCombinedContextAndFormItems(
		contextAlbums,
		albumAsArray
	);

	const formStations = watch("stations");
	const stations = useCombinedContextAndFormItems(
		contextStations,
		formStations
	);

	const artistMapper = useIdMapper(artists);
	const albumMapper = useIdMapper(albums);
	const stationMapper = useIdMapper(stations);

	return (<Loader status={callStatus} error={state.error}>
		<Box sx={inputField}>
			<Typography variant="h1">
				Edit a song
			</Typography>
			<Typography>
				Path: {songFilePath}
			</Typography>
			<Box>
				{canDownloadSongs && ids.length === 1 &&
					<Button href={getDownloadAddress(ids[0])}>Download</Button>}
			</Box>
			<Box sx={inputField}>
				{ids?.length > 1 && <TouchedCheckbox
					name="name"
				/>}
				<FormTextField
					name="name"
					formMethods={formMethods}
					label="Name"
					disabled={!canEditSongs}
				/>
			</Box>
			<Box>
				<Loader status={artistCallStatus} artistError={artistError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="primaryArtist"
						/>}
						<ArtistSelect
							name="primaryArtist"
							options={artists}
							formMethods={formMethods}
							label="Primary Artist"
							classes={{
								root: "dropdown-field",
							}}
							transform={{input: artistMapper}}
							disabled={!canEditSongs}
						/>
					</Box>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="artists"
						/>}
						<ArtistSelect
							name="artists"
							options={artists}
							formMethods={formMethods}
							label="Artists"
							transform={{input: artistMapper}}
							classes={{
								root: "dropdown-field",
							}}
							multiple
							disabled={!canEditSongs}
						/>
					</Box>
					{canEditSongs && <Box sx={inputField}>
						<ArtistNewModalOpener add={addArtist} />
					</Box>}
				</Loader>
			</Box>
			<Box>
				<Loader status={albumCallStatus} artistError={albumError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="album"
						/>}
						<AlbumSelect
							name="album"
							options={albums}
							formMethods={formMethods}
							label="Album"
							transform={{input: albumMapper }}
							classes={{
								root: "dropdown-field",
							}}
							disabled={!canEditSongs}
						/>
					</Box>
					{canEditSongs && <Box sx={inputField}>
						<AlbumNewModalOpener
							add={addAlbum}
							formArtists={formAllArtists}
						/>
					</Box>}
				</Loader>
			</Box>
			<Box>
				<Loader status={stationCallStatus} artistError={stationError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="stations"
						/>}
						<StationSelect
							name="stations"
							options={stations}
							formMethods={formMethods}
							label="Stations"
							transform={{input: stationMapper}}
							classes={{
								root: "dropdown-field",
							}}
							multiple
							disabled={!canEditSongs}
						/>
					</Box>
					{canEditSongs && <Box sx={inputField}>
						<StationNewModalOpener add={addStation} />
					</Box>}
				</Loader>
			</Box>
			<Box sx={inputField}>
				{ids?.length > 1 && <TouchedCheckbox
					name="genre"
				/>}
				<FormTextField
					name="genre"
					formMethods={formMethods}
					label="Genre"
					disabled={!canEditSongs}
				/>
			</Box>
			{canEditSongs && <Box sx={inputField} >
				<Button onClick={callSubmit}>
					Submit
				</Button>
			</Box>}
		</Box>
	</Loader>);
};