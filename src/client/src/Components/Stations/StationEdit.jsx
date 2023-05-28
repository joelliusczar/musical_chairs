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
import { DomRoutes, CallStatus } from "../../constants";
import {
	useStationData,
} from "../../Context_Providers/AppContextProvider";
import { useCurrentUser } from "../../Context_Providers/AuthContext";
import { Loader } from "../Shared/Loader";


const inputField = {
	margin: 2,
};

const initialValues = {
	name: "",
	displayName: "",
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
	const { handleSubmit, reset } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const stationId = values.id || null;
			const data = await saveStation({ values, id: stationId });
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