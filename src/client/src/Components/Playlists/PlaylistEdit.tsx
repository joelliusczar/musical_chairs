import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import {
	add as addPlaylist,
} from "../../API_Calls/playlistCalls";
import { useForm, UseFormReturn } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import {
	RulePriorityLevel,
} from "../../constants";
import { FormSelect } from "../Shared/FormSelect";
import {
	PlaylistInfo,
	PlaylistInfoForm,
} from "../../Types/playlist_types";
import { SubmitButton } from "../Shared/SubmitButton";


const inputField = {
	margin: 2,
};

const viewSecurityOptions = [
	{
		id: RulePriorityLevel.PUBLIC,
		name: "Public",
	},
	{
		id: RulePriorityLevel.ANY_USER,
		name: "Any User",
	},
	{
		id: RulePriorityLevel.INVITED_USER,
		name: "Invited Users Only",
	},
	{
		id: RulePriorityLevel.OWENER_USER,
		name: "Private",
	},
];




type PlaylistEditProps = {
	onCancel?: (e: unknown) => void
	formMethods: UseFormReturn<PlaylistInfoForm>,
	callSubmit: (e: React.BaseSyntheticEvent) => Promise<void>,
};

export const PlaylistEdit = (props: PlaylistEditProps) => {
	const { onCancel, formMethods, callSubmit } = props;

	const { watch, formState } = formMethods;

	const savedId = watch("id");

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

	const formMethods = useForm<PlaylistInfoForm>({
		defaultValues: {
			name: "",
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = addPlaylist({
				data: {
					name: values.name,
					description: values.description,
					viewsecuritylevel: values.viewsecuritylevel.id,
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
