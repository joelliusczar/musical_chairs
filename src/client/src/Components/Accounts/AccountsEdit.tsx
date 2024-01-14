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
	fetchUser,
	updateAccountBasic,
	updatePassword,
} from "../../API_Calls/userCalls";
import {
	useVoidWaitingReducer,
	voidDispatches as dispatches,
} from "../../Reducers/voidWaitingReducer";
import { useParams } from "react-router-dom";
import Loader from "../Shared/Loader";
import {
	PasswordUpdate,
	User,
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
		if (!pathVars.userkey) {
			enqueueSnackbar("User is missing", { variant: "error"});
			return;
		}
		try {
			const requestObj = updatePassword({
				subjectuserkey: pathVars.userkey, 
				...values,
			});
			await requestObj.call();
			enqueueSnackbar("Password updated successfully", { variant: "success"});
		}
		catch(err){
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});

	const formMethods = useForm<User>({
		defaultValues: {
			displayname: "",
			email: "",
		},
		resolver: yupResolver(schema),
		mode: "onBlur",
	});
	const { handleSubmit, reset, watch, formState } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const requestObj = updateAccountBasic(
				{subjectuserkey: values.id, data: values}
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
		const [ formId, formUsername] = watch(["id", "username"]);
		const key = pathVars.userKey;
		const isNumKey = Number.isInteger(key);
		const isStrKey = typeof key === "string";
		const isDiffId = isNumKey && parseInt(key || "") !== formId;
		const isDiffName = isStrKey && key != formUsername;
		if (!key || (!isDiffId && !isDiffName)) {
			return;
		}
		const requestObj = fetchUser({ subjectuserkey: key });
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
	},[dispatch, pathVars.userKey, watch, enqueueSnackbar, reset]);

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