import React, { useEffect, useReducer, useCallback } from "react";
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
	waitingReducer,
	dispatches,
} from "../Shared/waitingReducer";
import { InitialState } from "../../Types/reducer_types";
import { useParams } from "react-router-dom";
import Loader from "../Shared/Loader";

const inputField = {
	margin: 2,
};

const passwordSchema = Yup.object().shape({
	oldPassword: Yup.string().required("Old Password is required"),
	newPassword: Yup.string().required("New Password is required").min(6),
	passwordConfirm: Yup.string().required().test(
		"passwordConfirm",
		() => "Passwords must match",
		(value, context) => {
			return value === context.parent.newPassword;
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
	const [state, dispatch] = useReducer(waitingReducer(), InitialState);
	const pathVars = useParams();



	const passwordFormMethods = useForm({
		defaultValues: {
			oldPassword: "",
			newPassword: "",
			passwordConfirm: "",
		},
		resolver: yupResolver(passwordSchema),
		mode: "onBlur",
	});
	const { handleSubmit: passwordHandleSubmit } = passwordFormMethods;
	const passwordCallSubmit = passwordHandleSubmit(async values => {
		try {
			await updatePassword({userKey: pathVars.userKey, ...values});
			enqueueSnackbar("Password updated successfully", { variant: "success"});
		}
		catch(err){
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});

	const formMethods = useForm({
		defaultValues: {
			displayName: "",
			email: "",
		},
		resolver: yupResolver(schema),
		mode: "onBlur",
	});
	const { handleSubmit, reset, watch } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const data = await updateAccountBasic({userKey: values.id, data: values});
			reset(data);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err){
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});

	const _fetchUser = useCallback(async (params) => {
		try {
			dispatch(dispatches.started());
			const data = await fetchUser(params);
			reset(data);
			dispatch(dispatches.done());
		}
		catch (err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			dispatch(dispatches.failed(formatError(err)));
		}
	}, [dispatch, reset]);

	useEffect(() => {
		const [ formId, formUsername] = watch(["id", "username"]);
		const fetch = async () => {
			try {
				const key = pathVars.userKey;
				const isNumKey = Number.isInteger(key) === "number";
				const isStrKey = typeof key === "string";
				const isDiffId = isNumKey && key !== formId;
				const isDiffName = isStrKey && key != formUsername;
				if (isDiffId || isDiffName) {
					_fetchUser({ userKey: key });
				}

			}
			catch(err) {
				dispatch(dispatches.failed(formatError(err)));
			}
		};
		fetch();
	},[dispatch, pathVars.userKey, _fetchUser, watch]);

	return (<Loader status={state.callStatus} error={state.error}>
		<Box sx={inputField}>
			<Typography variant="h1">
				Edit an account
			</Typography>
		</Box>
		<Box>
			<Box sx={inputField}>
				<FormTextField
					name="oldPassword"
					label="Old Password"
					type="password"
					formMethods={passwordFormMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="newPassword"
					label="Password"
					type="password"
					formMethods={passwordFormMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="passwordConfirm"
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
					name="displayName"
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
				<Button onClick={callSubmit}>
					Submit
				</Button>
			</Box>
		</Box>
	</Loader>);
};