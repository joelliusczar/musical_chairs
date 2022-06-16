import React from "react";
import { useHistory } from "react-router-dom";
import { Box, Typography, Button } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import * as Yup from "yup";
import { createAccount, checkValues } from "./accounts_slice";
import debouncePromise from "debounce-promise";
import { useSnackbar } from "notistack";
import { DomRoutes } from "../../constants";



const inputField = {
	margin: 2,
};


export function AccountsNew() {
	const { enqueueSnackbar } = useSnackbar();
	const urlHistory = useHistory();

	const validatePhraseIsUnused = async (value, context) => {
		const used = await checkValues({ values: {
			[context.path]: value,
		}});
		return !(context.path in used) || !used[context.path];
	};

	const formik = useFormik({
		initialValues: {
			username: "",
			displayName: "",
			password: "",
			passwordConfirm: "",
			email: "",
		},
		onSubmit: async (values) => {
			try {
				await createAccount({ values });
				urlHistory.push(DomRoutes.accountsLogin);
				enqueueSnackbar("Save successful", { variant: "success"});
			}
			catch(err){
				enqueueSnackbar(err.response.data.detail[0].msg, { variant: "error"});
			}
		},
		validationSchema: Yup.object().shape({
			username: Yup.string().required().test(
				"username",
				(value) => `${value.path} is already used`,
				debouncePromise(validatePhraseIsUnused, 100)
			),
			password: Yup.string().required().min(6),
			passwordConfirm: Yup.string().required().test(
				"passwordConfirm",
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
		}),
	});

	return (
		<FormikProvider value={formik}>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create an account
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="username"
					label="User Name"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="displayName"
					label="Display Name"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="password"
					label="Password"
					type="password"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="passwordConfirm"
					label="Confirm Password"
					type="password"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="email"
					label="Email"
				/>
			</Box>
			<Box sx={inputField} >
				<Button onClick={formik.submitForm}>
					Submit
				</Button>
			</Box>

		</FormikProvider>
	);
}