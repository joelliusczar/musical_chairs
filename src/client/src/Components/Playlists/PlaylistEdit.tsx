import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import {
	Calls,
} from "../../API_Calls/playlistCalls";
import { useForm, UseFormReturn } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import { FormSelect } from "../Shared/FormSelect";
import {
	PlaylistInfo,
	PlaylistInfoForm,
} from "../../Types/playlist_types";
import { SubmitButton } from "../Shared/SubmitButton";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { validatePhraseIsUnused, viewSecurityOptions } from "./common";
import Loader from "../Shared/Loader";
import { StationTypes } from "../../constants";
import { StationInfo } from "../../Types/station_types";
import { StationSelect } from "../Stations/StationSelect";
import { StationNewModalOpener } from "../Stations/StationEdit";
import { useCombinedContextAndFormItems } from "../../Helpers/array_helpers";
import {
	useIdMapper,
	useStationData,
} from "../../Context_Providers/AppContext/AppContext";


const inputField = {
	margin: 2,
};


type PlaylistEditProps = {
	onCancel?: (e: unknown) => void
	formMethods: UseFormReturn<PlaylistInfoForm>,
	callSubmit: (e: React.BaseSyntheticEvent) => Promise<void>,
	formStations?: StationInfo[],
};

export const PlaylistEdit = (props: PlaylistEditProps) => {
	const { 
		onCancel,
		formMethods,
		callSubmit,
		formStations = [],
	 } = props;

	const { watch, formState } = formMethods;

	const savedId = watch("id");

	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		add: addStation,
	} = useStationData();

	const stations = useCombinedContextAndFormItems(
		contextStations,
		formStations
	).filter(s => 
		s.typeid === StationTypes.PLAYLISTS_ONLY || 
			s.typeid === StationTypes.ALBUMS_AND_PLAYLISTS
	);
	const stationMapper = useIdMapper(stations);

	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					{savedId ? "Edit" : "Create"} a playlist
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="name"
					label="Name"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="description"
					label="Description"
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
			<Box sx={inputField}>
				<FormSelect
					name="viewsecuritylevel"
					label="Who can see this playlist?"
					sx={{ width: 250 }}
					options={viewSecurityOptions}
					formMethods={formMethods}
					isOptionEqualToValue={(option, value) => {
						return option.id === value.id;
					}}
					defaultValue={viewSecurityOptions[0]}
					disableClearable={true}
				/>
			</Box>
			<Box sx={inputField} >
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
				>
					Submit
				</SubmitButton>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</>
	);
};


type PlaylistNewModalOpenerProps = {
	add?: (s: PlaylistInfo) => void;
}


export const PlaylistNewModalOpener = (props: PlaylistNewModalOpenerProps) => {

	const { add } = props;
	const { enqueueSnackbar } = useSnackbar();

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: PlaylistInfo) => {
		add && add(item);
		closeModal();
	};

	const schema = Yup.object().shape({
		name: Yup.string().required()
			.matches(/^[a-zA-Z0-9_]*$/, "Name can only contain a-zA-Z0-9_")
			.test(
				"name",
				(value) => `${value.path} is already used`,
				validatePhraseIsUnused
			),
	});

	const formMethods = useForm<PlaylistInfoForm>({
		defaultValues: {
			name: "",
			viewsecuritylevel: viewSecurityOptions[0],
			stations: [],
		},
		reValidateMode: "onSubmit",
		resolver: yupResolver(schema),
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = Calls.add({
				data: {
					name: values.name,
					description: values.description,
					viewsecuritylevel: values.viewsecuritylevel.id,
					stations: values.stations,
				},
			});
			const playlist = await requestObj.call();
			itemCreated(playlist);
			enqueueSnackbar("Save successful", { variant: "success" });
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error" });
			console.error(err);
		}
	});

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Playlist</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<PlaylistEdit
					onCancel={closeModal}
					callSubmit={callSubmit}
					formMethods={formMethods}
				/>
			</Dialog>
		</>);
};

export default PlaylistEdit;
