import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import { saveArtist } from "../../API_Calls/songInfoCalls";
import { useForm, UseFormReturn } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import { ArtistInfo } from "../../Types/song_info_types";
import { SubmitButton  } from "../Shared/SubmitButton";


const inputField = {
	margin: 2,
};

type ArtistEditProps = {
	formMethods: UseFormReturn<ArtistInfo>,
	onCancel?: (e: unknown) => void
	callSubmit: (e: React.BaseSyntheticEvent) => Promise<void>,
};

export const ArtistEdit = (props: ArtistEditProps) => {
	const { formMethods, callSubmit, onCancel } = props;

	const { formState } = formMethods;

	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Add an artist
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField<ArtistInfo>
					name="name"
					label="Name"
					formMethods={formMethods}
					onKeyUp={e => {
						if (e.code === "Enter") {
							callSubmit(e);
						}
					}}
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


type ArtistNewModalOpenerProps = {
	add?: (a: ArtistInfo) => void;
}

export const ArtistNewModalOpener = (props: ArtistNewModalOpenerProps) => {

	const { add } = props;
	const { enqueueSnackbar } = useSnackbar();

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: ArtistInfo) => {
		add && add(item);
		closeModal();
	};


	const formMethods = useForm<ArtistInfo>({
		defaultValues: {
			name: "",
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = saveArtist({ name: values.name });
			const artist = await requestObj.call();
			enqueueSnackbar("Save successful", { variant: "success"});
			itemCreated(artist);
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Artist</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<ArtistEdit 
					onCancel={closeModal}
					formMethods={formMethods}
					callSubmit={callSubmit}
				/>
			</Dialog>
		</>);
};
