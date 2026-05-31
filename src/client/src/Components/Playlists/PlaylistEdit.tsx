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
import { yupResolver } from "@hookform/resolvers/yup";
import { viewSecurityOptions } from "./common";
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
import { UserRoleDef } from "../../constants";
import { anyConformsToAnyRule } from "../../Helpers/rule_helpers";
import {
	useHasAnyRoles,
	useCurrentUser,
} from "../../Context_Providers/AuthContext/AuthContext";
import { playlistFormSchema } from "../../Types/Validation_Types/playlist";


const inputField = {
	margin: 2,
};


type PlaylistEditProps = {
	onCancel?: (e: unknown) => void,
	referenceRecord: PlaylistInfo,
	formMethods: UseFormReturn<PlaylistInfoForm>,
	callSubmit: (e: React.BaseSyntheticEvent) => Promise<void>,
	formStations?: StationInfo[],
};

export const PlaylistEdit = (props: PlaylistEditProps) => {
	const { 
		onCancel,
		referenceRecord,
		formMethods,
		callSubmit,
		formStations = [],
	 } = props;

	const { formState } = formMethods;

	const savedId = referenceRecord.id;
	const playlistRules = referenceRecord.rules;

	const canCreatePlaylists = useHasAnyRoles([
		UserRoleDef.PLAYLIST_CREATE,
	]);
	const canEditPlaylist = () => {
		if(savedId) {
			return anyConformsToAnyRule(
				playlistRules, [UserRoleDef.PLAYLIST_EDIT]
			);
		}
		else {
			return canCreatePlaylists;
		}
	};


	const {
		items: contextStations,
		callStatus: stationCallStatus,
		error: stationError,
		add: addStation,
	} = useStationData();

	const stations = useCombinedContextAndFormItems(
		contextStations,
		formStations
	).filter(s => s.typeid === StationTypes.ALBUMS_AND_PLAYLISTS);
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
					disabled={!canEditPlaylist()}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="displayname"
					label="Display Name"
					formMethods={formMethods}
					disabled={!canEditPlaylist()}
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
							disabled={!canEditPlaylist()}
						/>
					</Box>
					<>
						{canEditPlaylist() && <Box sx={inputField}>
							<StationNewModalOpener add={addStation} />
						</Box>}
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
					disabled={!canEditPlaylist()}
				/>
			</Box>
			<Box sx={inputField} >
				{canEditPlaylist() && <SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
				>
					Submit
				</SubmitButton>}
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
	const currentUser = useCurrentUser();

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: PlaylistInfo) => {
		add && add(item);
		closeModal();
	};

	const formMethods = useForm<PlaylistInfoForm>({
		defaultValues: {
			name: "",
			viewsecuritylevel: viewSecurityOptions[0],
			stations: [],
		},
		reValidateMode: "onSubmit",
		resolver: yupResolver(playlistFormSchema),
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = Calls.add({
				data: {
					name: values.name,
					displayname: values.displayname || "",
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
					referenceRecord={{
						id: "",
						name: "",
						displayname: "",
						viewsecuritylevel: viewSecurityOptions[0].id,
						owner: currentUser,
						rules: [],
					}}
				/>
			</Dialog>
		</>);
};

export default PlaylistEdit;
