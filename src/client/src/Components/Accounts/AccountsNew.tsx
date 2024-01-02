import React from "react";
import { useNavigate } from "react-router-dom";
import { Box, Typography } from "@mui/material";
import { useForm } from "react-hook-form";
import { FormTextField } from "../Shared/FormTextField";
import * as Yup from "yup";
import { createAccount } from "../../API_Calls/userCalls";
import debouncePromise from "debounce-promise";
import { useSnackbar } from "notistack";
import { DomRoutes } from "../../constants";
import { yupResolver } from "@hookform/resolvers/yup";
import { formatError } from "../../Helpers/error_formatter";
import { validatePhraseIsUnused } from "../../Helpers/validation_helpers";
import { UserCreationInfo } from "../../Types/user_types";
import { SubmitButton } from "../Shared/SubmitButton";


const inputField = {
	margin: 2,
};

const schema = Yup.object().shape({
	username: Yup.string().required().test(
		"username",
		(value) => `${value.path} is already used`,
		debouncePromise(validatePhraseIsUnused, 100)
	),
	password: Yup.string().required().min(6),
	passwordconfirm: Yup.string().required().test(
		"passwordconfirm",
		() => "Passwords must match",
		(value, context) => {
			return value === context.parent.password;
		}
	),
	email: Yup.string().required().email().test(
		"email",
		(value) => `${value.path} is already used`,
		debouncePromise(validatePhraseIsUnused, 100)
	),
});


export function AccountsNew() {
	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();


	const formMethods = useForm<UserCreationInfo>({
		defaultValues: {
			username: "",
			displayname: "",
			password: "",
			passwordconfirm: "",
			email: "",
		},
		resolver: yupResolver(schema),
		mode: "onBlur",
	});
	const { handleSubmit, formState } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			await createAccount({ values });
			navigate(DomRoutes.accountsLogin());
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err){
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});


	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create an account
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="username"
					label="User Name"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="displayname"
					label="Display Name"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="password"
					label="Password"
					type="password"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="passwordconfirm"
					label="Confirm Password"
					type="password"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="email"
					label="Email"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField} >
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
				>
					Submit
				</SubmitButton>
			</Box>

		</>
	);
}