import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { saveTag } from "./tagsService";

const inputField = {
	margin: 2,
};

export const TagNew = (props) => {
	const { afterSubmit, onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();

	const formik = useFormik({
		initialValues: {
			tagName: "",
		},
		onSubmit: async (values) => {
			try {
				const tag = await saveTag({ tagName:values.tagName });
				enqueueSnackbar("Save successful", { variant: "success"});
				afterSubmit(tag);
			}
			catch(err) {
				enqueueSnackbar(err.response.data.detail[0].msg, { variant: "error"});
				console.error(err);
			}
		},
	});

	return (
		<FormikProvider value={formik}>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a tag
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="tagName"
					label="Name"
				/>
			</Box>
			<Box sx={inputField} >
				<Button onClick={formik.submitForm}>
					Submit
				</Button>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</FormikProvider>
	);
};

TagNew.propTypes = {
	afterSubmit: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
};