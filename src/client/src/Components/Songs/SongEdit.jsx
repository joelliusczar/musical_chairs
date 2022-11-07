import React, { useReducer, useEffect } from "react";
import { Box, Typography, Button, Checkbox } from "@mui/material";
import { makeStyles } from "@mui/styles";
import * as Yup from "yup";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { FormSelect } from "../Shared/FormSelect";
import { FormTextField } from "../Shared/FormTextField";
import {
	useArtistData,
	useAlbumData,
	useStationData,
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


const inputField = {
	margin: 2,
};

const useStyles = makeStyles(() => ({
	dropdownField: {
		minWidth: 195,
		display: "inline-block",
	},
}));

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
});

export const SongEdit = () => {

	const { enqueueSnackbar } = useSnackbar();
	const [state, dispatch] = useReducer(waitingReducer(), initialState);
	const { callStatus } = state;
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const ids = queryObj.getAll("id").map(id => parseInt(id));
	const classes = useStyles();

	const {
		items: artists,
		callStatus: artistCallStatus,
		error: artistError,
		add: addArtist,
		idMapper: artistMapper,
	} = useArtistData();

	const {
		items: albums,
		callStatus: albumCallStatus,
		error: albumError,
		add: addAlbum,
		idMapper: albumMapper,
	} = useAlbumData();

	const {
		items: stations,
		callStatus: stationCallStatus,
		error: stationError,
		add: addStation,
		idMapper: stationMapper,
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

	return (<Loader status={callStatus} error={state.error}>
		<Box sx={inputField}>
			<Typography variant="h1">
				Edit a song
			</Typography>
			<Typography>
				Path: {songFilePath}
			</Typography>
			<Box sx={inputField}>
				{ids?.length > 1 && <TouchedCheckbox
					name="name"
				/>}
				<FormTextField
					name="name"
					formMethods={formMethods}
					label="Name"
				/>
			</Box>
			<Box>
				<Loader status={artistCallStatus} artistError={artistError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="primaryArtist"
						/>}
						<FormSelect
							name="primaryArtist"
							options={artists}
							formMethods={formMethods}
							label="Primary Artist"
							classes={{
								root: classes.dropdownField,
							}}
							transform={{input: artistMapper}}
						/>
					</Box>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="artists"
						/>}
						<FormSelect
							name="artists"
							options={artists}
							formMethods={formMethods}
							label="Artists"
							transform={{input: artistMapper}}
							classes={{
								root: classes.dropdownField,
							}}
							multiple
						/>
					</Box>
					<Box sx={inputField}>
						<ArtistNewModalOpener add={addArtist} />
					</Box>
				</Loader>
			</Box>
			<Box>
				<Loader status={albumCallStatus} artistError={albumError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="album"
						/>}
						<FormSelect
							name="album"
							getOptionLabel={(option) => option ?
								`${option.name}${option.albumArtist?.name ?
									` - ${option.albumArtist?.name}` : ""}` : ""}
							options={albums}
							formMethods={formMethods}
							label="Album"
							transform={{input: albumMapper }}
							classes={{
								root: classes.dropdownField,
							}}
						/>
					</Box>
					<Box sx={inputField}>
						<AlbumNewModalOpener add={addAlbum} />
					</Box>
				</Loader>
			</Box>
			<Box>
				<Loader status={stationCallStatus} artistError={stationError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="stations"
						/>}
						<FormSelect
							name="stations"
							options={stations}
							formMethods={formMethods}
							label="Stations"
							transform={{input: stationMapper}}
							classes={{
								root: classes.dropdownField,
							}}
							multiple
						/>
					</Box>
					<Box sx={inputField}>
						<StationNewModalOpener add={addStation} />
					</Box>
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
				/>
			</Box>
			<Box sx={inputField} >
				<Button onClick={callSubmit}>
					Submit
				</Button>
			</Box>
		</Box>
	</Loader>);
};