import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { saveTag } from "../../API_Calls/tagCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";

const inputField = {
	margin: 2,
};

export const TagEdit = (props) => {
	const { afterSubmit, onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();

	const formMethods = useForm({
		defaultValues: {
			tagName: "",
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const tag = await saveTag({ tagName:values.tagName });
			enqueueSnackbar("Save successful", { variant: "success"});
			afterSubmit(tag);
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
					Create a tag
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="tagName"
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

TagEdit.propTypes = {
	afterSubmit: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
};


export const TagNewModalOpener = (props) => {

	const { add } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item) => {
		add && add(item);
		closeModal();
	};

	return (
		<>
			<Box sx={inputField}>
				<Button onClick={() => setItemNewOpen(true)}>Add New Tag</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal}>
				<TagEdit afterSubmit={itemCreated} onCancel={closeModal} />
			</Dialog>
		</>);
};

TagNewModalOpener.propTypes = {
	add: PropTypes.func,
};