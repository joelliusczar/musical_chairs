import React, { useState, useEffect } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import {
	saveStation,
	checkValues,
	fetchStationForEdit,
} from "../../API_Calls/stationCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useNavigate, useParams } from "react-router-dom";
import {
	dispatches,
} from "../../Reducers/waitingReducer";
import { useVoidWaitingReducer } from "../../Reducers/voidWaitingReducer";
import {
	DomRoutes,
	CallStatus,
	MinItemSecurityLevel,
} from "../../constants";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import {
	useCurrentUser,
	useAuthViewStateChange,
} from "../../Context_Providers/AuthContext";
import { Loader } from "../Shared/Loader";
import { FormSelect } from "../Shared/FormSelect";
import {
	StationInfo,
	StationInfoForm,
} from "../../Types/station_types";
import { SubmitButton } from "../Shared/SubmitButton";



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
	const used = await checkValues({ id, values: {
		[context.path]: value,
	}});
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


	const [state, dispatch] = useVoidWaitingReducer();
	const { callStatus, error } = state;
	const {
		add: addStation,
		update: updateStation,
	} = useStationData();

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
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset, watch, formState } = formMethods;
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
			const data = await saveStation({ values: saveData, id: stationId });
			afterSubmit(data);
			if (stationId) {
				updateStation(stationId, data);
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

	useAuthViewStateChange(dispatch);

	useEffect(() => {
		const fetch = async () => {
			try {
				if(pathVars.stationkey && pathVars.ownerkey) {
					if(!callStatus) {
						dispatch(dispatches.started());
						const data = await fetchStationForEdit({
							ownerkey: pathVars.ownerkey,
							stationkey: pathVars.stationkey,
						});
						const formData = stationInfoToFormData(data);
						reset(formData);
						dispatch(dispatches.done());
					}
				}
				else {
					reset(initialValues);
				}
			}
			catch(err) {
				enqueueSnackbar(formatError(err), { variant: "error"});
				dispatch(dispatches.failed(formatError(err)));
			}
		};

		fetch();
	}, [
		dispatch,
		callStatus,
		pathVars.ownerkey,
		pathVars.stationkey,
	]);

	const loadStatus = pathVars.stationkey ? callStatus: CallStatus.done;
	const viewSecurityLevel = watch("viewsecuritylevel");
	const bannedRequestLevels = viewSecurityOptions.filter(o =>
		o.id < viewSecurityLevel.id || o.id === MinItemSecurityLevel.PUBLIC
	).reduce<{[id: number]: boolean}>((accumulator, current) => {
		accumulator[current.id] = true;
		return accumulator;
	}, {});

	const savedId = watch("id");

	return (
		<Loader status={loadStatus} error={error}>
			<Box sx={inputField}>
				<Typography variant="h1">
					{savedId ? "Edit" : "Create"} a station
				</Typography>
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
			<Box>

			</Box>
			<Box sx={inputField} >
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


