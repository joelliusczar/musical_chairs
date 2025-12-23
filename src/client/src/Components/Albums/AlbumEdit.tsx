import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import { add as saveAlbum } from "../../API_Calls/albumCalls";
import { useForm, UseFormReturn } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import {
	useArtistData,
	useIdMapper,
	useStationData,
} from "../../Context_Providers/AppContext/AppContext";
import { ArtistNewModalOpener } from "../Artists/ArtistEdit";
import Loader from "../Shared/Loader";
import { useCombinedContextAndFormItems } from "../../Helpers/array_helpers";
import { ArtistSelect } from "../Artists/ArtistSelect";
import { AlbumInfo, ArtistInfo } from "../../Types/song_info_types";
import { SubmitButton } from "../Shared/SubmitButton";
import { StationTypes } from "../../constants";
import { StationInfo } from "../../Types/station_types";
import { StationSelect } from "../Stations/StationSelect";
import { StationNewModalOpener } from "../Stations/StationEdit";

const inputField = {
	margin: 2,
};


type AlbumEditProps = {
	id?: number
	formMethods: UseFormReturn<AlbumInfo>
	onCancel?: (e: unknown) => void
	callSubmit: (e: React.BaseSyntheticEvent) => Promise<void>,
	formArtists?: ArtistInfo[]
	formStations?: StationInfo[]
};


export const AlbumEdit = (
	props: AlbumEditProps
) => {
	const { 
		id, 
		formMethods, 
		callSubmit, 
		onCancel, 
		formArtists = [],
		formStations = [],
	} = props;
	

	const {
		items: contextArtists,
		callStatus: artistCallStatus,
		error: artistError,
		add: addArtist,
	} = useArtistData();

	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		add: addStation,
	} = useStationData();


	const { formState } = formMethods;
	
	const artists = useCombinedContextAndFormItems(
		contextArtists,
		formArtists
	);
	const artistMapper = useIdMapper(artists);

	const stations = useCombinedContextAndFormItems(
		contextStations,
		formStations
	).filter(s => 
		s.typeid === StationTypes.ALBUMS_ONLY || 
			s.typeid === StationTypes.ALBUMS_AND_PLAYLISTS
	);
	const stationMapper = useIdMapper(stations);

	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					{!!id ? "Edit" : "Add"} an album
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="name"
					label="Name"
					formMethods={formMethods}
				/>
			</Box>
			<Loader status={artistCallStatus} error={artistError}>
				<Box sx={inputField}>
					<ArtistSelect
						name="albumartist"
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
			<Box sx={inputField}>
				<FormTextField
					name="versionnote"
					label="Version Note"
					formMethods={formMethods}
				/>
			</Box>
			<Box>
				<Loader status={stationCallStatus} error={stationError}>
					<Box sx={inputField}>
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
						/>
					</Box>
					<>
						<Box sx={inputField}>
							<StationNewModalOpener add={addStation} />
						</Box>
					</>
				</Loader>
			</Box>
			<Box sx={inputField} >
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}>
					Submit
				</SubmitButton>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</>
	);
};


type AlbumNewModalOpenerProps = {
	add?: (a: AlbumInfo) => void
	formArtists: ArtistInfo[]
	formStations: StationInfo[]
};

export const AlbumNewModalOpener = (props: AlbumNewModalOpenerProps) => {

	const { add, formArtists, formStations } = props;
	const { enqueueSnackbar } = useSnackbar();

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: AlbumInfo) => {
		add && add(item);
		closeModal();
	};

	const formMethods = useForm<AlbumInfo>({
		defaultValues: {
			name: "",
			albumartist: null,
			versionnote: "",
			stations: [],
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = saveAlbum({ data: {
				name: values.name,
				year: values.year || undefined,
				albumartist: values.albumartist || undefined,
				stations: values.stations,
				versionnote: values.versionnote,
			} });
			const album = await requestObj.call();
			enqueueSnackbar("Save successful", { variant: "success"});
			itemCreated(album);
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Album</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<AlbumEdit
					formMethods={formMethods}
					callSubmit={callSubmit}
					onCancel={closeModal}
					formArtists={formArtists}
					formStations={formStations}
				/>
			</Dialog>
		</>);
};
