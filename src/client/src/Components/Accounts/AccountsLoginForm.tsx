import React from "react";
import { Box, Button, Typography } from "@mui/material";
import { useForm } from "react-hook-form";
import { FormTextField } from "../Shared/FormTextField";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import { useLogin } from "../../Context_Providers/AuthContext";

export function LoginForm(props) {

	const { afterSubmit, onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();
	const [ login ] = useLogin();

	const formMethods = useForm({
		defaultValues: {
			username: "",
			password: "",
		},
	});
	const { handleSubmit } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			await login(values.username, values.password);
			enqueueSnackbar("Login successful", { variant: "success"});
			afterSubmit();
		}
		catch(error) {
			enqueueSnackbar("Login unsuccessful", { variant: "error"});
			console.error(error);
		}
	});



	return (
		<Box sx={{ p: 1 }}>
			<Typography variant="h1">Login</Typography>
			<Link
				onClick={onCancel}
				to={`${DomRoutes.accountsNew()}`}
			>
				Create new account
			</Link>
			<Box sx={{ m: 1}}>
				<FormTextField
					label="User Name"
					formMethods={formMethods}
					name="username"
				/>
			</Box>
			<Box sx={{ m: 1}}>
				<FormTextField
					formMethods={formMethods}
					label="Password"
					name="password"
					type="password"
				/>
			</Box>
			<Box>
				<Button onClick={callSubmit}>
					Submit
				</Button>
				{onCancel &&<Button onClick={onCancel}>
					Cancel
				</Button>}
			</Box>
		</Box>
	);
}

LoginForm.propTypes = {
	afterSubmit: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
};

