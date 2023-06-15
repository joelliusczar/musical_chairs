import React, { useState, useReducer, useEffect } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import PropTypes from "prop-types";
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
import { useHistory, useParams } from "react-router-dom";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Shared/waitingReducer";
import {
	DomRoutes,
	CallStatus,
	MinItemSecurityLevel,
} from "../../constants";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import { useCurrentUser } from "../../Context_Providers/AuthContext";
import { Loader } from "../Shared/Loader";
import { FormSelect } from "../Shared/FormSelect";


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
	displayName: "",
	viewSecurityLevel: viewSecurityOptions[0],
	requestSecurityLevel: requestSecurityOptions[1],
};

const validatePhraseIsUnused = async (value, context) => {
	const id = context?.parent?.id;
	const used = await checkValues({ values: {
		id,
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
	requestSecurityLevel: Yup.object().required().test(
		"requestSecurityLevel",
		"Request Security cannot be public or lower than view security",
		(value, context) => {
			return value !== MinItemSecurityLevel.PUBLIC
				&& value.id >= context.parent.viewSecurityLevel.id;
		}
	),
});



export const StationEdit = (props) => {
	const { onCancel } = props;
	const { enqueueSnackbar } = useSnackbar();
	const urlHistory = useHistory();
	const pathVars = useParams();
	const currentUser = useCurrentUser();


	const [state, dispatch] = useReducer(waitingReducer(), initialState);
	const { callStatus, error } = state;
	const {
		add: addStation,
		update: updateStation,
	} = useStationData();

	const getPageUrl = (params) => {
		return DomRoutes.stationsEdit({
			ownerKey: pathVars.ownerKey || currentUser.username,
			stationKey: params.name,
		});
	};

	const _afterSubmit = (data) => {
		reset(data);
		urlHistory.replace(getPageUrl({ name: data.name }));
	};

	const afterSubmit = props.afterSubmit || _afterSubmit;


	const formMethods = useForm({
		defaultValues: initialValues,
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset, watch } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const stationId = values.id || null;
			const {viewSecurityLevel, requestSecurityLevel, ...saveData} = values;
			saveData.viewSecurityLevel = viewSecurityLevel.id;
			saveData.requestSecurityLevel = requestSecurityLevel.id;
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

	useEffect(() => {
		const fetch = async () => {
			try {
				if(pathVars.stationKey) {
					if(!callStatus) {
						dispatch(dispatches.started());
						const data = await fetchStationForEdit({
							ownerKey: pathVars.ownerKey,
							stationKey: pathVars.stationKey,
						});
						const viewSecurityLevel = viewSecurityOptions
							.filter(o => o.id === data.viewSecurityLevel);
						const requestSecurityLevel = viewSecurityOptions
							.filter(o => o.id === data.requestSecurityLevel);
						data.viewSecurityLevel =
							viewSecurityLevel.length ?
								viewSecurityLevel[0] : viewSecurityOptions[0];
						data.requestSecurityLevel =
							requestSecurityLevel.length ?
								requestSecurityLevel[0] : viewSecurityOptions[1];
						reset(data);
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
		pathVars.ownerKey,
		pathVars.stationKey,
	]);

	const loadStatus = pathVars.stationKey ? callStatus: CallStatus.done;
	const viewSecurityLevel = watch("viewSecurityLevel");
	const bannedRequestLevels = viewSecurityOptions.filter(o =>
		o.id < viewSecurityLevel.id || o.id === MinItemSecurityLevel.PUBLIC
	).reduce((accumulator, current) => {
		accumulator[current.id] = true;
		return accumulator;
	}, {});



	return (
		<Loader status={loadStatus} error={error}>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a station
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
					name="displayName"
					label="Display Name"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField}>
				<FormSelect
					name="viewSecurityLevel"
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
					name="requestSecurityLevel"
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
				<Button onClick={callSubmit}>
					Submit
				</Button>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</Loader>
	);
};

StationEdit.propTypes = {
	afterSubmit: PropTypes.func,
	onCancel: PropTypes.func,
};


export const StationNewModalOpener = (props) => {

	const { add } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item) => {
		add && add(item);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Station</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal}>
				<StationEdit
					afterSubmit={itemCreated}
					onCancel={closeModal}
				/>
			</Dialog>
		</>);
};

StationNewModalOpener.propTypes = {
	add: PropTypes.func,
};