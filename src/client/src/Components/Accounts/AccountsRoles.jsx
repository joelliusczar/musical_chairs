import React, { useEffect, useState } from "react";
import { Box, Button, Chip } from "@mui/material";
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

const tmpModOptions = ["0", "5", "10", "15", "30", "60", "1440"].map(value => ({
	id: value,
	name: value === "0" ? "": value,
}));

const roleDefs = Object.keys(UserRoleDef).map(key => ({
	id: UserRoleDef[key],
	name: UserRoleDef[key],
}));
roleDefs.unshift({
	id: "",
	name: "",
});

const defaultFormData = {
	accountInfo: {
		roles: [],
	},
	tmpRole: roleDefs[0],
	tmpRoleMod: tmpModOptions[0],
};



export const AccountsRoles = () => {
	const { id } = useParams();
	const { enqueueSnackbar } = useSnackbar();
	const [fetchStatus, setFetchStatus] = useState();
	//const [saveStatus, setSaveStatus] = useState();
	const [fetchError, setFetchError] = useState(null);
	const currentUser = useCurrentUser();




	const formMethods = useForm({
		defaultValues: defaultFormData,
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
				...defaultFormData,
				accountInfo: data,
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
		const moddedRole = {
			name: role.name,
			count: 1,
			span: mod.id * 1,
			priority: 0,
		};
		const idx = watchAll.accountInfo.roles
			.findIndex(r => conformsToRole(r.name, role));
		if(idx === -1) {
			if(role === UserRoleDef.ADMIN) {
				setValue("accountInfo.roles", [{
					name: UserRoleDef.ADMIN,
					count: 1,
					span: 0,
					priority: 0,
				}]);
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
					const data = await fetchUser({ userKey: id });
					reset({
						...defaultFormData,
						accountInfo: data,
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
								label={role.name}
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
						options={roleDefs}
						isOptionEqualToValue={(option, value) => {
							return option.id === value.id;
						}}
					/>
					{watchAll.tmpRole &&
						watchAll.tmpRole !== UserRoleDef.ADMIN &&
					<FormSelect
						label="Mod"
						name="tmpRoleMod"
						sx={{ width: 100 }}
						formMethods={formMethods}
						options={tmpModOptions}
						isOptionEqualToValue={(option, value) => {
							return option.id === value.id;
						}}
					/>}
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