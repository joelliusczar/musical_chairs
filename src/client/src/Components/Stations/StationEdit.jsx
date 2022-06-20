import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";

const inputField = {
	margin: 2,
};

export const StationEdit = () => {

	const formik = useFormik({});

	return (
		<FormikProvider value={formik}>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a station
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="stationName"
					label="Internal Name"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="displayName"
					label="Display Name"
				/>
			</Box>
			<Box sx={inputField} >
				<Button onClick={formik.submitForm}>
					Submit
				</Button>
			</Box>
		</FormikProvider>
	);
};