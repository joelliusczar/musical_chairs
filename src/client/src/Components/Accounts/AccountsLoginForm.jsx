import React from "react";
import { Box, Button, Typography } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import PropTypes from "prop-types";
import { login } from "./accounts_slice";
import { useDispatch } from "react-redux";
import { useSnackbar } from "notistack";

export function LoginForm(props) {

	const { afterSubmit, onCancel } = props;
	const dispatch = useDispatch();
	const { enqueueSnackbar } = useSnackbar();

	const formik = useFormik({
		initialValues: {
			username: "",
			password: "",
		},
		onSubmit: async (values) => {
			try {
				await dispatch(
					login({username: values.username, password: values.password})
				).unwrap();
				enqueueSnackbar("Login successful", { variant: "success"});
				afterSubmit();
			}
			catch(error) {
				enqueueSnackbar("Login unsuccessful", { variant: "error"});
				console.error(error);
			}
		},
	});

	const handleCancel = () => {
		onCancel && onCancel();
	};

	return (
		<FormikProvider value={formik}>
			<Box sx={{ p: 1 }}>
				<Typography variant="h1">Login</Typography>
				<Box sx={{ m: 1}}>
					<FormikTextField
						label="User Name"
						name="username"
					/>
				</Box>
				<Box sx={{ m: 1}}>
					<FormikTextField
						label="Password"
						name="password"
						type="password"
					/>
				</Box>
				<Box>
					<Button onClick={formik.submitForm}>
						Save
					</Button>
					<Button onClick={handleCancel}>
						Cancel
					</Button>
				</Box>
			</Box>
		</FormikProvider>
	);
}

LoginForm.propTypes = {
	afterSubmit: PropTypes.func,
	onCancel: PropTypes.func,
};

