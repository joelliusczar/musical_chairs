import React, { useReducer, useEffect } from "react";
import { Box, Typography, Button } from "@mui/material";
import * as Yup from "yup";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { FormSelect } from "../Shared/FormSelect";
import { FormTextField } from "../Shared/FormTextField";
import {
	useArtistData,
	useAlbumData,
	useTagData,
} from "../../Context_Providers/AppContextProvider";
import Loader from "../Shared/Loader";
import { ArtistNewModalOpener } from "../Artists/ArtistEdit";
import { AlbumNewModalOpener } from "../Albums/AlbumEdit";
import { TagNewModalOpener } from "../Tags/TagEdit";
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
} from "../../API_Calls/songInfoCalls";
import { formatError } from "../../Helpers/error_formatter";


const inputField = {
	margin: 2,
};

const schema = Yup.object().shape({
});

export const SongEdit = () => {

	const { enqueueSnackbar } = useSnackbar();
	const [state, dispatch] = useReducer(waitingReducer(), initialState);
	const { callStatus } = state;
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const id = queryObj.get("id");

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
		items: tags,
		callStatus: tagCallStatus,
		error: tagError,
		add: addTag,
		idMapper: tagMapper,
	} = useTagData();

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
			tags: [],
			genre: "",
		},
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset, watch } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const data = await saveSongEdits({ id, data: values });
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
				if(id) {
					if(!callStatus) {
						dispatch(dispatches.started());
						const data = await fetchSongForEdit({
							id,
						});
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
	}, [dispatch, callStatus, id ]);

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
				<FormTextField
					name="name"
					formMethods={formMethods}
					label="Name"
				/>
			</Box>
			<Box>
				<Loader status={artistCallStatus} artistError={artistError}>
					<Box sx={inputField}>
						<FormSelect
							name="primaryArtist"
							options={artists}
							formMethods={formMethods}
							label="Primary Artist"
							sx={{ minWidth: 195 }}
							transform={{input: artistMapper}}
						/>
					</Box>
					<Box sx={inputField}>
						<FormSelect
							name="artists"
							options={artists}
							formMethods={formMethods}
							label="Artists"
							transform={{input: artistMapper}}
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
						<FormSelect
							name="album"
							getOptionLabel={(option) => option ?
								`${option.name}${option.albumArtist?.name ?
									` - ${option.albumArtist?.name}` : ""}` : ""}
							options={albums}
							formMethods={formMethods}
							label="Album"
							transform={{input: albumMapper }}
						/>
					</Box>
					<Box sx={inputField}>
						<AlbumNewModalOpener add={addAlbum} />
					</Box>
				</Loader>
			</Box>
			<Box>
				<Loader status={tagCallStatus} artistError={tagError}>
					<Box sx={inputField}>
						<FormSelect
							name="tags"
							options={tags}
							formMethods={formMethods}
							label="Tags"
							transform={{input: tagMapper}}
							multiple
						/>
					</Box>
					<Box sx={inputField}>
						<TagNewModalOpener add={addTag} />
					</Box>
				</Loader>
			</Box>
			<Box sx={inputField}>
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