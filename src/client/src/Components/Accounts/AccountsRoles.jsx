import React, { useEffect, useState } from "react";
import { FormikProvider, useFormik } from "formik";
import { Box, MenuItem, Button, Chip } from "@mui/material";
import { useParams } from "react-router-dom";
import { useSnackbar } from "notistack";
import { UserRoleDef } from "../../constants";
import { FormikSelect } from "../Shared/FormikSelect";
import { NotFound } from "../Shared/RoutingErrors";
import { updateUserRoles, fetchUser } from "./accounts_slice";
import { CallStatus } from "../../constants";
import Loader from "../Shared/Loader";
import { useCurrentUser } from "./AuthContext";


const inputField = {
	margin: 2,
};

export const AccountsRoles = () => {
	const { id } = useParams();
	const { enqueueSnackbar } = useSnackbar();
	const [fetchStatus, setFetchStatus] = useState();
	//const [saveStatus, setSaveStatus] = useState();
	const [fetchError, setFetchError] = useState(null);
	const currentUser = useCurrentUser();

	const formik = useFormik({
		initialValues: {
			accountInfo: {
				roles: [],
			},
			tmpRole: "",
			tmpRoleMod: "",
		},
		onSubmit: async (values, { resetForm }) => {
			try {
				const data = await updateUserRoles({
					id,
					roles: values.accountInfo.roles,
					currentUser,
				});
				enqueueSnackbar("Save successful", { variant: "success"});
				resetForm({
					values: {
						accountInfo: data,
						tmpRole: "",
						tmpRoleMod: "",
					},
				});
			}
			catch(err) {
				enqueueSnackbar(err.response.data.detail[0].msg, { variant: "error"});
			}
		},
	});

	const { resetForm } = formik;

	const addRole = () => {
		const role = formik.values.tmpRole;
		const mod = formik.values.tmpRoleMod;
		const moddedRole = mod ? `${role}:${mod}` : role;
		const oldRoles = formik.values.accountInfo.roles;
		const idx = oldRoles.findIndex(r => r.startsWith(role));
		if(idx === -1) {
			if(role === UserRoleDef.ADMIN) {
				formik.setFieldValue("accountInfo.roles", [UserRoleDef.ADMIN]);
				return;
			}
			const roles = [...formik.values.accountInfo.roles, moddedRole];
			formik.setFieldValue("accountInfo.roles", roles);
		}
		else {
			enqueueSnackbar(`A value of ${role} is already present in list. ` +
				"Please remove first before adding", { variant: "warning"});
		}
	};

	const removeRole = (idx) => {
		const roles = [...formik.values.accountInfo.roles];
		roles.splice(idx, 1);
		formik.setFieldValue("roles", roles);
	};

	useEffect(() => {
		const fetch = async (id) => {
			try {
				if(!fetchStatus && id) {
					setFetchStatus(CallStatus.loading);
					const data = await fetchUser({ id });
					resetForm({
						values: {
							accountInfo: data,
							tmpRole: "",
							tmpRoleMod: "",
						}});
				}
			}
			catch(err) {
				setFetchError(err.response.data.detail[0].msg);
			}
			finally {
				setFetchStatus(CallStatus.done);
			}

		};
		fetch(id);
	},[fetchStatus, setFetchStatus, id, fetchUser, resetForm]);

	if(!id) {
		return <NotFound />;
	}

	return (
		<FormikProvider value={formik} >
			<Loader status={fetchStatus} error={fetchError}>
				<Box sx={inputField}>
					{(formik.values.accountInfo.roles || []).map((role, idx) => {
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
						disabled={!formik.values.tmpRole}
						onClick={addRole}
					>
						Add Role
					</Button>
				</Box>
				<Box sx={inputField} >
					<Button onClick={formik.submitForm}>
						Submit
					</Button>
				</Box>
			</Loader>
		</FormikProvider>
	);
};