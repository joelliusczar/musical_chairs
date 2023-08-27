import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { saveArtist } from "../../API_Calls/songInfoCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import { ArtistInfo } from "../../Types/song_info_types";

const inputField = {
	margin: 2,
};

type ArtistEditProps = {
	onCancel: (e: unknown) => void
	afterSubmit: (a: ArtistInfo) => void
};

export const ArtistEdit = (props: ArtistEditProps) => {
	const { afterSubmit, onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();

	const formMethods = useForm<ArtistInfo>({
		defaultValues: {
			name: "",
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const artist = await saveArtist({ name: values.name });
			enqueueSnackbar("Save successful", { variant: "success"});
			afterSubmit(artist);
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});

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
				/>
			</Box>
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

ArtistEdit.propTypes = {
	afterSubmit: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
};

type ArtistNewModalOpenerProps = {
	add?: (a: ArtistInfo) => void;
}

export const ArtistNewModalOpener = (props: ArtistNewModalOpenerProps) => {

	const { add } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: ArtistInfo) => {
		add && add(item);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Artist</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<ArtistEdit afterSubmit={itemCreated} onCancel={closeModal} />
			</Dialog>
		</>);
};
