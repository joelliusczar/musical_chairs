import React from "react";
import { Box, MenuItem, Typography, Button, Chip } from "@mui/material";
import { useParams } from "react-router-dom";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import * as Yup from "yup";
import { createAccount, checkValues, isAdminSelector } from "./accounts_slice";
import debouncePromise from "debounce-promise";
import { UserRoleDef } from "../../constants";
import { FormikSelect } from "../Shared/FormikSelect";
import { useSnackbar } from "notistack";
import { useSelector } from "react-redux";
import { currentUserSelector } from "./accounts_slice";
import { GoToNotFound } from "../Shared/NotFound";


const inputField = {
	margin: 2,
};


export function AccountEdit() {
	const { id } = useParams();
	const { enqueueSnackbar } = useSnackbar();
	const isAdmin = useSelector(isAdminSelector);
	const currentUser = useSelector(currentUserSelector);

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
			roles: [],
			tmpRole: "",
			tmpRoleMod: "",
		},
		onSubmit: async (values) => {
			if(id) {
				console.log("placeholder");
			}
			else {
				const response = await createAccount({ values });
				console.log(response);
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

	const addRole = () => {
		const role = formik.values.tmpRole;
		const mod = formik.values.tmpRoleMod;
		const moddedRole = mod ? `${role}:${mod}` : role;
		const oldRoles = formik.values.roles;
		const idx = oldRoles.findIndex(r => r.startsWith(role));
		if(idx === -1) {
			const roles = [...formik.values.roles, moddedRole];
			formik.setFieldValue("roles", roles);
		}
		else {
			enqueueSnackbar(`A value of ${role} is already present in list. ` +
				"Please remove first before adding", { variant: "warning"});
		}
	};

	const removeRole = (idx) => {
		const roles = [...formik.values.roles];
		roles.splice(idx, 1);
		formik.setFieldValue("roles", roles);
	};

	if(currentUser.username && !id) {
		return <GoToNotFound />;
	}

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
			{isAdmin && <>
				<Box sx={inputField}>
					{(formik.values.roles || []).map((role, idx) => {
						return (
							<Chip
								key={`role_${idx}`}
								label={role}
								color="primary"
								onDelete={() => removeRole(idx)}
								sx={{ m: 1 }}
							/>
						);
					})}
				</Box>
				<Box sx={inputField}>
					<FormikSelect
						name="tmpRole"
						label="Roles"
						sx={{ width: 195 }}
					>
						{Object.keys(UserRoleDef).map((key) => {
							return (
								<MenuItem key={`role_${key}`} value={UserRoleDef[key]}>
									{UserRoleDef[key]}
								</MenuItem>
							);
						})}
					</FormikSelect>
					{formik.values.tmpRole &&
						formik.values.tmpRole !== UserRoleDef.ADMIN &&
					<FormikSelect
						label="Mod"
						name="tmpRoleMod"
						sx={{ width: 100 }}
					>
						<MenuItem key={"mod_empty"} value={""}>
							None
						</MenuItem>
						{["5", "10", "15", "30", "60", "1440"].map((value) => {
							return (
								<MenuItem key={`mod_${value}`} value={value}>
									{value}
								</MenuItem>
							);
						})}
					</FormikSelect>}
					<Button
						onClick={addRole}
					>
						Add Role
					</Button>
				</Box>
			</>}
			<Box sx={inputField} >
				<Button onClick={formik.submitForm}>
					Submit
				</Button>
			</Box>

		</FormikProvider>
	);
}