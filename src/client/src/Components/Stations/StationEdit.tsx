import React, { useState, useEffect, useCallback } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import {
	saveCaller,
	checkValuesCaller,
	getRecordCaller,
	removeRecordCaller,
	copyRecordCaller,
} from "../../API_Calls/stationCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useNavigate, useParams } from "react-router-dom";
import {
	useDataWaitingReducer,
	dataDispatches as dispatches,
} from "../../Reducers/dataWaitingReducer";
import { RequiredDataStore } from "../../Reducers/reducerStores";
import {
	DomRoutes,
	CallStatus,
	MinItemSecurityLevel,
} from "../../constants";
import {
	useStationData,
} from "../../Context_Providers/AppContext/AppContext";
import {
	useCurrentUser,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext/AuthContext";
import { Loader } from "../Shared/Loader";
import { FormSelect } from "../Shared/FormSelect";
import {
	StationInfo,
	StationInfoForm,
} from "../../Types/station_types";
import { SubmitButton } from "../Shared/SubmitButton";
import { isCallPending } from "../../Helpers/request_helpers";
import { YesNoModalOpener } from "../Shared/YesNoControl";


const inputField = {
	margin: 2,
};

const viewSecurityOptions = [
	{
		id: MinItemSecurityLevel.PUBLIC,
		name: "Public",
	},
	{
		id: MinItemSecurityLevel.ANY_USER,
		name: "Any User",
	},
	{
		id: MinItemSecurityLevel.INVITED_USER,
		name: "Invited Users Only",
	},
	{
		id: MinItemSecurityLevel.OWENER_USER,
		name: "Private",
	},
];

const requestSecurityOptions = viewSecurityOptions;

const initialValues = {
	name: "",
	displayname: "",
	viewsecuritylevel: viewSecurityOptions[0],
	requestsecuritylevel: requestSecurityOptions[1],
};



const validatePhraseIsUnused = async (
	value: string | undefined,
	context: Yup.TestContext<Partial<StationInfoForm>>
) => {
	const id = context?.parent?.id;
	if (!value) return true;
	const requestObj = checkValuesCaller({ id, values: {
		[context.path]: value,
	}});
	const used = await requestObj.call();
	return !(context.path in used) || !used[context.path];
};

const schema = Yup.object().shape({
	name: Yup.string().required().test(
		"name",
		(value) => `${value.path} is already used`,
		validatePhraseIsUnused
	),
	requestsecuritylevel: Yup.object().required().test(
		"requestsecuritylevel",
		"Request Security cannot be public or lower than view security",
		(value, context) => {
			return (value.id) !== MinItemSecurityLevel.PUBLIC
				&& value.id >= context.parent.viewsecuritylevel.id;
		}
	),
});

const stationInfoToFormData = (data: StationInfo) => {
	const viewSecurityLevel = viewSecurityOptions
		.filter(o => o.id === data.viewsecuritylevel);
	const requestSecurityLevel = viewSecurityOptions
		.filter(o => o.id === data.requestsecuritylevel);
	const formData = {
		...data,
		viewsecuritylevel: viewSecurityLevel.length ?
			viewSecurityLevel[0] : viewSecurityOptions[0],
		requestsecuritylevel: requestSecurityLevel.length ?
			requestSecurityLevel[0] : viewSecurityOptions[1],
	};
	return formData;
};

type StationEditProps = {
	onCancel?: (e: unknown) => void
	afterSubmit?: (s: StationInfo) => void
};

export const StationEdit = (props: StationEditProps) => {
	const { onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();
	const navigate = useNavigate();
	const pathVars = useParams();
	const currentUser = useCurrentUser();


	const [state, dispatch] = useDataWaitingReducer<StationInfo>(
		new RequiredDataStore({
			id: 0,
			name: "",
			displayname: "",
			isrunning: false,
			owner: {
				id: 0,
				username: "",
				email: "",
				roles: [],
			},
			rules: [],
			viewsecuritylevel: 0,
			requestsecuritylevel: 0,
		})
	);
	const { callStatus, error } = state;
	const {
		add: addStation,
		update: updateStation,
		remove: removeStation,
	} = useStationData();
	const isPending = isCallPending(callStatus);

	const getPageUrl = (params: { name: string }) => {
		return DomRoutes.stationsEdit({
			ownerkey: pathVars.ownerkey || currentUser.username,
			stationkey: params.name,
		});
	};

	const _afterSubmit = (data: StationInfo) => {
		reset(stationInfoToFormData(data));
		navigate(getPageUrl({ name: data.name }), { replace: true});
	};

	const afterSubmit = props.afterSubmit || _afterSubmit;


	const formMethods = useForm<StationInfoForm>({
		defaultValues: initialValues,
		reValidateMode: "onSubmit",
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset, watch, formState, getValues } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const stationId = values.id || null;
			const {viewsecuritylevel, requestsecuritylevel } = values;
			const saveData = {
				...values,
				viewsecuritylevel: viewsecuritylevel.id,
				requestsecuritylevel: requestsecuritylevel.id,
			};
			saveData.viewsecuritylevel = viewsecuritylevel.id;
			saveData.requestsecuritylevel = requestsecuritylevel.id;
			const requestObj = saveCaller({ values: saveData, id: stationId });
			const data = await requestObj.call();
			afterSubmit(data);
			if (stationId) {
				updateStation(data);
			}
			else {
				addStation(data);
			}
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});
	const callSubmitCopy = handleSubmit(async values => {
		try {
			const stationId = values.id;
			if (!stationId) {
				console.error("Station id is missing");
				return;
			}
			const {viewsecuritylevel, requestsecuritylevel } = values;
			const saveData = {
				...values,
				viewsecuritylevel: viewsecuritylevel.id,
				requestsecuritylevel: requestsecuritylevel.id,
			};
			saveData.viewsecuritylevel = viewsecuritylevel.id;
			saveData.requestsecuritylevel = requestsecuritylevel.id;
			const requestObj = copyRecordCaller({ values: saveData, id: stationId });
			const data = await requestObj.call();
			afterSubmit(data);
			addStation(data);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});

	const savedId = watch("id");

	const canCopyRecord = () => {
		if (!savedId) return false;
		return true;
	};

	const canDeleteItem = () => {
		const ownerkey = pathVars.ownerkey?.trim();
		if (currentUser.username === ownerkey) return true;
		return false;
	};

	const deleteRecord = async () => {
		try {
			if (!savedId) return;

			const requestObj = removeRecordCaller({  id: savedId });
			await requestObj.call();
			removeStation(state.data);
			navigate(DomRoutes.stations(), { replace: true });
		}
		catch (err) {
			enqueueSnackbar(formatError(err),{ variant: "error"});
		}
	};


	const authReset = useCallback(() => {
		dispatch(dispatches.restart());
	}, [dispatch]);

	useAuthViewStateChange(authReset);

	useEffect(() => {
		if(pathVars.stationkey && pathVars.ownerkey) {
			const requestObj = getRecordCaller({
				ownerkey: pathVars.ownerkey,
				stationkey: pathVars.stationkey,
			});
			if (!isPending) return;
			const fetch = async () => {
				try {
					dispatch(dispatches.started());
					const data = await requestObj.call();
					const formData = stationInfoToFormData(data);
					reset(formData);
					dispatch(dispatches.done(data));
				}
				catch(err) {
					enqueueSnackbar(formatError(err), { variant: "error"});
					dispatch(dispatches.failed(formatError(err)));
				}
			};
			fetch();
			return () => requestObj.abortController.abort();
		}
		else {
			reset(initialValues);
		}
	}, [
		dispatch,
		isPending,
		pathVars.ownerkey,
		pathVars.stationkey,
		enqueueSnackbar,
		reset,
	]);

	const loadStatus = pathVars.stationkey ? callStatus: CallStatus.done;
	const viewSecurityLevel = watch("viewsecuritylevel");
	const bannedRequestLevels = viewSecurityOptions.filter(o =>
		o.id < viewSecurityLevel.id || o.id === MinItemSecurityLevel.PUBLIC
	).reduce<{[id: number]: boolean}>((accumulator, current) => {
		accumulator[current.id] = true;
		return accumulator;
	}, {});


	return (
		<Loader status={loadStatus} error={error}>
			<Box sx={inputField}>
				<Typography variant="h1">
					{savedId ? "Edit" : "Create"} a station
				</Typography>
			</Box>
			<Box>
				{canDeleteItem() && <YesNoModalOpener
					promptLabel="Delete Station"
					message={`Are you sure you want to delete ${""}?`}
					onYes={() => deleteRecord()}
					onNo={() => {}}
				/>}
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="name"
					label="Name"
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
				<FormSelect
					name="viewsecuritylevel"
					label="Who can see this radio station?"
					sx={{ width: 250 }}
					options={viewSecurityOptions}
					formMethods={formMethods}
					isOptionEqualToValue={(option, value) => {
						return option.id === value.id;
					}}
					defaultValue={viewSecurityOptions[0]}
				/>
			</Box>
			<Box sx={inputField}>
				<FormSelect
					name="requestsecuritylevel"
					label="Who can request on this radio station?"
					sx={{ width: 250 }}
					options={viewSecurityOptions.slice(1)}
					formMethods={formMethods}
					isOptionEqualToValue={(option, value) => {
						return option.id === value.id;
					}}
					defaultValue={viewSecurityOptions[1]}
					getOptionDisabled={o => o.id in bannedRequestLevels}
				/>
			</Box>
			<Box sx={inputField} >
				{canCopyRecord() && <YesNoModalOpener
					promptLabel="Copy Station"
					message={`Are you sure you want to Copy ${""}?`}
					onYes={callSubmitCopy}
					onNo={() => {}}
					disabled={!formState.isDirty}
				/>}
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
				>
					Submit
				</SubmitButton>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</Loader>
	);
};


type StationNewModalOpenerProps = {
	add?: (s: StationInfo) => void;
}


export const StationNewModalOpener = (props: StationNewModalOpenerProps) => {

	const { add } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: StationInfo) => {
		add && add(item);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Station</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<StationEdit
					afterSubmit={itemCreated}
					onCancel={closeModal}
				/>
			</Dialog>
		</>);
};

export default StationEdit;
