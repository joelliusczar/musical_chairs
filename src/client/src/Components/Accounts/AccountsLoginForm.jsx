import React from "react";
import { Box, Button, Typography } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import { useLogin } from "./AuthContext";

export function LoginForm(props) {

	const { afterSubmit, onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();
	const [ login ] = useLogin();

	const formik = useFormik({
		initialValues: {
			username: "",
			password: "",
		},
		onSubmit: async (values) => {
			try {
				await login(values.username, values.password);
				enqueueSnackbar("Login successful", { variant: "success"});
				afterSubmit();
			}
			catch(error) {
				enqueueSnackbar("Login unsuccessful", { variant: "error"});
				console.error(error);
			}
		},
	});


	return (
		<FormikProvider value={formik}>
			<Box sx={{ p: 1 }}>
				<Typography variant="h1">Login</Typography>
				<Link
					onClick={onCancel}
					to={`${DomRoutes.accountsNew}`}
				>
					Create new account
				</Link>
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
						Submit
					</Button>
					{onCancel &&<Button onClick={onCancel}>
						Cancel
					</Button>}
				</Box>
			</Box>
		</FormikProvider>
	);
}

LoginForm.propTypes = {
	afterSubmit: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
};

