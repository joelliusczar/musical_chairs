import React, { useEffect, useState } from "react";
import { Box, MenuItem, Button, Chip } from "@mui/material";
import { useParams } from "react-router-dom";
import { useSnackbar } from "notistack";
import { UserRoleDef } from "../../constants";
import { FormSelect } from "../Shared/FormSelect";
import { NotFound } from "../Shared/RoutingErrors";
import { updateUserRoles, fetchUser } from "../../API_Calls/userCalls";
import { CallStatus } from "../../constants";
import Loader from "../Shared/Loader";
import {
	useCurrentUser,
	conformsToRole,
} from "../../Context_Providers/AuthContext";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";


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

	const formMethods = useForm({
		defaultValues: {
			accountInfo: {
				roles: [],
			},
			tmpRole: "",
			tmpRoleMod: "",
		},
	});
	const { handleSubmit, reset, setValue, watch } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const data = await updateUserRoles({
				id,
				roles: values.accountInfo.roles,
				currentUser,
			});
			enqueueSnackbar("Save successful", { variant: "success"});
			reset({
				accountInfo: data,
				tmpRole: "",
				tmpRoleMod: "",
			});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});
	const watchAll = watch();

	const addRole = () => {
		const role = watchAll.tmpRole;
		const mod = watchAll.tmpRoleMod;
		const moddedRole = mod ? `${role}:${mod}` : role;
		const idx = watchAll.accountInfo.roles
			.findIndex(r => conformsToRole(r, role));
		if(idx === -1) {
			if(role === UserRoleDef.ADMIN) {
				setValue("accountInfo.roles", [UserRoleDef.ADMIN]);
				return;
			}
			const roles = [...watchAll.accountInfo.roles, moddedRole];
			setValue("accountInfo.roles", roles);
		}
		else {
			enqueueSnackbar(`A value of ${role} is already present in list. ` +
				"Please remove first before adding", { variant: "warning"});
		}
	};

	const removeRole = (idx) => {
		const roles = [...watchAll.accountInfo.roles];
		roles.splice(idx, 1);
		setValue("accountInfo.roles", roles);
	};

	useEffect(() => {
		const fetch = async (id) => {
			try {
				if(!fetchStatus && id) {
					setFetchStatus(CallStatus.loading);
					const data = await fetchUser({ id });
					reset({
						accountInfo: data,
						tmpRole: "",
						tmpRoleMod: "",
					});
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
	},[fetchStatus, setFetchStatus, id, fetchUser, reset]);

	if(!id) {
		return <NotFound />;
	}

	return (
		<>
			<Loader status={fetchStatus} error={fetchError}>
				<Box sx={inputField}>
					{(watchAll.accountInfo.roles || []).map((role, idx) => {
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
					<FormSelect
						name="tmpRole"
						label="Roles"
						sx={{ width: 195 }}
						formMethods={formMethods}
					>
						{Object.keys(UserRoleDef).map((key) => {
							return (
								<MenuItem key={`role_${key}`} value={UserRoleDef[key]}>
									{UserRoleDef[key]}
								</MenuItem>
							);
						})}
					</FormSelect>
					{watchAll.tmpRole &&
						watchAll.tmpRole !== UserRoleDef.ADMIN &&
					<FormSelect
						label="Mod"
						name="tmpRoleMod"
						sx={{ width: 100 }}
						formMethods={formMethods}
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
					</FormSelect>}
					<Button
						disabled={!watchAll.tmpRole}
						onClick={addRole}
					>
						Add Role
					</Button>
				</Box>
				<Box sx={inputField} >
					<Button onClick={callSubmit}>
						Submit
					</Button>
				</Box>
			</Loader>
		</>
	);
};