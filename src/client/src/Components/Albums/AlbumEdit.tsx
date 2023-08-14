import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { saveAlbum } from "../../API_Calls/songInfoCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import {
	useArtistData,
	useIdMapper,
} from "../../Context_Providers/AppContextProvider";
import { ArtistNewModalOpener } from "../Artists/ArtistEdit";
import Loader from "../Shared/Loader";
import { useCombinedContextAndFormItems } from "../../Helpers/array_helpers";
import { ArtistSelect } from "../Artists/ArtistSelect";
import { AlbumInfo, ArtistInfo } from "../../Types/song_info_types";

const inputField = {
	margin: 2,
};

type AlbumEditProps = {
	onCancel: (e: unknown) => void
	afterSubmit: (a: AlbumInfo) => void
	formArtists: ArtistInfo[]
};


export const AlbumEdit = (props: AlbumEditProps) => {
	const { afterSubmit, onCancel, formArtists } = props;
	const { enqueueSnackbar } = useSnackbar();

	const {
		items: contextArtists,
		callStatus: artistCallStatus,
		error: artistError,
		add: addArtist,
	} = useArtistData();

	const formMethods = useForm<AlbumInfo>({
		defaultValues: {
			name: "",
			albumArtist: null,
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const album = await saveAlbum({ data: values });
			enqueueSnackbar("Save successful", { variant: "success"});
			afterSubmit(album);
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});

	const artists = useCombinedContextAndFormItems(
		contextArtists,
		formArtists
	);
	const artistMapper = useIdMapper(artists);

	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Add an album
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField<AlbumInfo>
					name="name"
					label="Name"
					formMethods={formMethods}
				/>
			</Box>
			<Loader status={artistCallStatus} error={artistError}>
				<Box sx={inputField}>
					<ArtistSelect<AlbumInfo>
						name="albumArtist"
						options={artists}
						formMethods={formMethods}
						label="Album Artist"
						sx={{ minWidth: 195 }}
						transform={{input: artistMapper}}
					/>
				</Box>
				<Box sx={inputField}>
					<ArtistNewModalOpener add={addArtist} />
				</Box>
			</Loader>
			<Box sx={inputField} >
				<Button onClick={callSubmit}>
					Submit
				</Button>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</>
	);
};

AlbumEdit.propTypes = {
	afterSubmit: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
	formArtists: PropTypes.arrayOf(PropTypes.shape({
		id: PropTypes.oneOfType([PropTypes.number,PropTypes.string]),
		name: PropTypes.string,
	})),
};

type AlbumNewModalOpenerProps = {
	add?: (a: AlbumInfo) => void
	formArtists: ArtistInfo[]
};

export const AlbumNewModalOpener = (props: AlbumNewModalOpenerProps) => {

	const { add, formArtists } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: AlbumInfo) => {
		add && add(item);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Album</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<AlbumEdit
					afterSubmit={itemCreated}
					onCancel={closeModal}
					formArtists={formArtists}
				/>
			</Dialog>
		</>);
};

AlbumNewModalOpener.propTypes = {
	add: PropTypes.func,
	formArtists: PropTypes.arrayOf(PropTypes.shape({
		id: PropTypes.oneOfType([PropTypes.number,PropTypes.string]),
		name: PropTypes.string,
	})),
};