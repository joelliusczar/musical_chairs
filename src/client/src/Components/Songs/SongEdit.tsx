import React, { useEffect, useMemo, useCallback } from "react";
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
} from "../../Context_Providers/AppContext/AppContext";
import Loader from "../Shared/Loader";
import { ArtistNewModalOpener } from "../Artists/ArtistEdit";
import { AlbumNewModalOpener } from "../Albums/AlbumEdit";
import { StationNewModalOpener } from "../Stations/StationEdit";
import { useLocation } from "react-router-dom";
import { 
	useVoidWaitingReducer,
	voidDispatches as dispatches,
} from "../../Reducers/voidWaitingReducer";
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
} from "../../Context_Providers/AuthContext/AuthContext";
import { UserRoleDef } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import {
	useCombinedContextAndFormItems,
} from "../../Helpers/array_helpers";
import { AlbumSelect } from "../Albums/AlbumSelect";
import { ArtistSelect } from "../Artists/ArtistSelect";
import { StationSelect } from "../Stations/StationSelect";
import {
	SongInfoForm,
	TouchTypes,
	TouchedObject,
} from "../../Types/song_info_types";
import { Named, IdValue } from "../../Types/generic_types";
import { SubmitButton } from "../Shared/SubmitButton";
import { isCallPending } from "../../Helpers/request_helpers";
import { getDownloadAddress } from "../../Helpers/request_helpers";


const inputField = {
	margin: 2,
};




const createTouchedObject = (touchedArr: string[]) => {
	const result: TouchedObject = {};
	if (!touchedArr) return result;
	for (const name of touchedArr) {
		result[name] = TouchTypes.set;
	}
	return result;
};

const touchedObjectToArr = (touchedObj: TouchedObject) => {
	const result: string[] = [];
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
	"primaryartist": Yup.object().nullable().test(
		"primaryartist",
		"Primary Artist is already listed.",
		(value, testContext: Yup.TestContext<Partial<SongInfoForm>>) => {
			const parent = testContext.parent as SongInfoForm;
			if (parent.artists?.some(a => a?.id === value?.id)) {
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
			const found: { [key: IdValue]: true} = {};
			for (const artist of value) {
				if (artist?.id === testContext.parent.primaryartist?.id) {
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
	const [state, dispatch] = useVoidWaitingReducer();
	const { callStatus } = state;
	const isPending = isCallPending(callStatus);
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

	const formMethods = useForm<SongInfoForm>({
		defaultValues: {
			name: "",
			artists: [],
			primaryartist: {
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
		getValues,
	} = formMethods;

	const songRules = watch("rules");
	const canEditSongs = anyConformsToAnyRule(
		songRules, [UserRoleDef.PATH_EDIT]
	);
	const multiSongTouchedField = watch("touched");

	const handleMutliSongTouchedCheck = (name: string) => {
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

	const isMultSongTouchedChecked = (name: string) => {
		if (!multiSongTouchedField) return false;
		const value = multiSongTouchedField[name];
		if (value === TouchTypes.edited || value === TouchTypes.set) return true;
		return false;
	};

	const downloadSong =  (songId: number) => {
		const url = getDownloadAddress(songId);
		window?.open(url, "_blank")?.focus();
	};

	// eslint-disable-next-line react/prop-types
	const TouchedCheckbox = ({ name }: Named) => {
		return <Checkbox
			name={name}
			onChange={() => handleMutliSongTouchedCheck(name)}
			checked={isMultSongTouchedChecked(name)}
			disabled={!canEditSongs}
		/>;
	};

	const callSubmit = handleSubmit(async values => {
		try {
			const valuesSavura = {
				...values,
				touched: touchedObjectToArr(values.touched),
			};
			const requestObj = ids.length < 2 ?
				saveSongEdits({ id: ids[0], data: valuesSavura }) :
				saveSongsEditsMulti({ ids, data: valuesSavura });
			const data = await requestObj.call();
			reset(data);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), {variant: "error" });
		}
	});

	const authReset = useCallback(() => {
		dispatch(dispatches.restart());
	}, [dispatch]);

	useAuthViewStateChange(authReset);

	useEffect(() => {
		if (ids.length === 0) {
			dispatch(dispatches.failed("No song selected"));
			return;
		}
		const requestObj = ids.length == 1 ?
			fetchSongForEdit({
				id: ids[0],
			}) :
			fetchSongsForMultiEdit({ ids });
		if (!isPending) return;
		const fetch = async () => {
			try {
				dispatch(dispatches.started());
				const data = await requestObj.call();
				reset({
					...data,
					touched: createTouchedObject(data.touched),
				});
				dispatch(dispatches.done());
			}
			catch(err) {
				dispatch(dispatches.failed(formatError(err)));
			}
		};

		fetch();

		return () => requestObj.abortController.abort();
	}, [dispatch, ids, reset, isPending ]);

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
	const primaryArtist = watch("primaryartist");
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
					<Button 
						onClick={() => downloadSong(ids[0])}
					>
						Download
					</Button>}
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
				<Loader status={artistCallStatus} error={artistError}>
					<Box sx={inputField}>
						{ids?.length > 1 && <TouchedCheckbox
							name="primaryartist"
						/>}
						<ArtistSelect
							name="primaryartist"
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
					<>
						{canEditSongs && <Box sx={inputField}>
							<ArtistNewModalOpener add={(artist) => {
								addArtist(artist);
								const primaryArtist = getValues("primaryartist");
								if (!primaryArtist) {
									setValue("primaryartist", artist);
								}
							}} />
						</Box>}
					</>
				</Loader>
			</Box>
			<Box>
				<Loader status={albumCallStatus} error={albumError}>
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
					<>
						{canEditSongs && <Box sx={inputField}>
							<AlbumNewModalOpener
								add={(album) => {
									addAlbum(album);
									setValue("album", album);
								}}
								formArtists={formAllArtists}
							/>
						</Box>}
					</>
				</Loader>
			</Box>
			<Box>
				<Loader status={stationCallStatus} error={stationError}>
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
					<>
						{canEditSongs && <Box sx={inputField}>
							<StationNewModalOpener add={addStation} />
						</Box>}
					</>
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
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}>
					Submit
				</SubmitButton>
			</Box>}
		</Box>
	</Loader>);
};

export default SongEdit;