import React, { useEffect } from "react";
import { Box, Typography, Button } from "@mui/material";
import { useSnackbar } from "notistack";
import { useForm } from "react-hook-form";
import { FormTextField } from "../Shared/FormTextField";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import debouncePromise from "debounce-promise";
import { validatePhraseIsUnused } from "../../Helpers/validation_helpers";
import { formatError } from "../../Helpers/error_formatter";
import {
	Calls,
} from "../../API_Calls/userCalls";
import {
	useVoidWaitingReducer,
	voidDispatches as dispatches,
} from "../../Reducers/voidWaitingReducer";
import { useParams } from "react-router-dom";
import Loader from "../Shared/Loader";
import {
	PasswordUpdate,
	UserBasicUpdate,
} from "../../Types/user_types";
import { SubmitButton } from "../Shared/SubmitButton";

const inputField = {
	margin: 2,
};

const passwordSchema = Yup.object().shape({
	oldpassword: Yup.string().required("Old Password is required"),
	newpassword: Yup.string().required("New Password is required").min(6),
	passwordconfirm: Yup.string().required().test(
		"passwordconfirm",
		() => "Passwords must match",
		(value, context) => {
			return value === context.parent.newpassword;
		}
	),
});

const schema = Yup.object().shape({
	email: Yup.string().required().email().test(
		"email",
		(value) => `${value.path} is already used`,
		debouncePromise(validatePhraseIsUnused, 100)
	),
});



export const AccountsEdit = () => {
	const { enqueueSnackbar } = useSnackbar();
	const [state, dispatch] = useVoidWaitingReducer();
	const pathVars = useParams();



	const passwordFormMethods = useForm<
		PasswordUpdate & { passwordconfirm: string }
	>({
		defaultValues: {
			oldpassword: "",
			newpassword: "",
			passwordconfirm: "",
		},
		resolver: yupResolver(passwordSchema),
		mode: "onBlur",
	});
	const { handleSubmit: passwordHandleSubmit } = passwordFormMethods;
	const passwordCallSubmit = passwordHandleSubmit(async values => {
		if (!pathVars.subjectuserkey) {
			enqueueSnackbar("User is missing", { variant: "error"});
			return;
		}
		try {
			const requestObj = Calls.updatePassword({
				subjectuserkey: pathVars.subjectuserkey, 
				...values,
			});
			await requestObj.call();
			enqueueSnackbar("Password updated successfully", { variant: "success"});
		}
		catch(err){
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});

	const formMethods = useForm<UserBasicUpdate>({
		defaultValues: {
			displayname: "",
			email: "",
		},
		resolver: yupResolver(schema),
		mode: "onBlur",
	});
	const { handleSubmit, reset, watch, formState } = formMethods;
	const callSubmit = handleSubmit(async values => {
		if (!pathVars.subjectuserkey) {
			enqueueSnackbar("Missing subject user key", { variant: "error"});
			return;
		}
		try {

			const requestObj = Calls.updateAccountBasic(
				{subjectuserkey: pathVars.subjectuserkey, data: values}
			);
			const data = await requestObj.call();
			reset(data);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err){
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});


	useEffect(() => {
		const requestObj = Calls.selfget();
		const fetch = async () => {
			try {
				dispatch(dispatches.started());
				const data = await requestObj.call();
				reset(data);
				dispatch(dispatches.done());
			}
			catch (err) {
				enqueueSnackbar(formatError(err), { variant: "error"});
				dispatch(dispatches.failed(formatError(err)));
			}
		};

		fetch();

		return () => requestObj.abortController.abort();
	},[dispatch, pathVars.subjectuserkey, watch, enqueueSnackbar, reset]);

	return (<Loader status={state.callStatus} error={state.error}>
		<Box sx={inputField}>
			<Typography variant="h1">
				Edit an account
			</Typography>
		</Box>
		<Box>
			<Box sx={inputField}>
				<FormTextField
					name="oldpassword"
					label="Old Password"
					type="password"
					formMethods={passwordFormMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="newpassword"
					label="Password"
					type="password"
					formMethods={passwordFormMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="passwordconfirm"
					label="Confirm Password"
					type="password"
					formMethods={passwordFormMethods}
				/>
			</Box>
			<Box sx={inputField} >
				<Button onClick={passwordCallSubmit}>
					Update Password
				</Button>
			</Box>
		</Box>
		<Box>
			<Box sx={inputField}>
				<FormTextField
					name="displayname"
					label="Display Name"
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
		</Box>
	</Loader>);
};

export default AccountsEdit;