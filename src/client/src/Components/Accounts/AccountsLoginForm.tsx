import React from "react";
import { Box, Button, Typography } from "@mui/material";
import { useForm } from "react-hook-form";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import { Link } from "react-router-dom";
import { DomRoutes } from "../../constants";
import {
	useLogin,
} from "../../Context_Providers/AuthContext/AuthContext";
import { SubmitButton } from "../Shared/SubmitButton";


type LoginFormProps = {
	afterSubmit: () => void,
	onCancel?: (e: unknown) => void
};


export function LoginForm(props: LoginFormProps) {

	const { afterSubmit, onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();
	const [ login ] = useLogin();

	const formMethods = useForm({
		defaultValues: {
			username: "",
			password: "",
		},
	});
	const { handleSubmit, formState } = formMethods;
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
					onKeyUp={e => {
						if (e.code === "Enter") {
							callSubmit(e);
						}
					}}
				/>
			</Box>
			<Box>
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
				>
					Submit
				</SubmitButton>
				{onCancel && <Button onClick={onCancel}>
					Cancel
				</Button>}
			</Box>
		</Box>
	);
}

export default LoginForm;