import React, { useReducer, useEffect } from "react";
import { Box, Typography, Button } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { TagAssignment } from "../Tags/TagAssignment";
import {
	saveStation,
	fetchStationForEdit,
	checkValues,
} from "../../API_Calls/stationCalls";
import { useSnackbar } from "notistack";
import { useHistory, useLocation } from "react-router-dom";
import { DomRoutes } from "../../constants";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Shared/waitingReducer";
import * as Yup from "yup";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { formatError } from "../../Helpers/error_formatter";



const inputField = {
	margin: 2,
};

const validatePhraseIsUnused = async (value, context) => {
	const used = await checkValues({ values: {
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

export const StationEdit = () => {
	const { enqueueSnackbar } = useSnackbar();
	const urlHistory = useHistory();
	const [state, dispatch] = useReducer(waitingReducer(), initialState);
	const { callStatus } = state;
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const id = queryObj.get("id");
	const nameQueryStr = queryObj.get("name");


	const formMethods = useForm({
		defaultValues: {
			name: "",
			displayName: "",
			tags: [],
		},
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const stationId = id ? id : values.id ? values.id : null;
			const data = await saveStation({ values, id: stationId });
			reset(data);
			dispatch(dispatches.done());
			urlHistory.replace(getPageUrl({ id: data.id }));
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
		}
	});

	const getPageUrl = (params) => {
		let queryStr = null;
		if(queryObj) {
			if(params.id) {
				queryObj.set("id", params.id);
			}
			if(params.name) {
				queryObj.set("rows", params.name);
			}
			queryStr = `?${queryObj.toString()}`;
		}
		return `${DomRoutes.stationsEdit}${queryStr}`;
	};

	useEffect(() => {
		const fetch = async () => {
			try {
				if(id || nameQueryStr) {
					if(!callStatus) {
						dispatch(dispatches.started());
						const data = await fetchStationForEdit({
							params: {
								id,
								name: nameQueryStr,
							},
						});
						reset(data);
						dispatch(dispatches.done());
					}
				}
				else {
					reset();
				}
			}
			catch(err) {
				dispatch(dispatches.failed(formatError(err)));
			}
		};

		fetch();
	}, [dispatch, callStatus, id, nameQueryStr]);


	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a station
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="name"
					formMethods={formMethods}
					label="Internal Name"
				/>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="displayName"
					formMethods={formMethods}
					label="Display Name"
				/>
			</Box>
			<TagAssignment name="tags" formMethods={formMethods}/>
			<Box sx={inputField} >
				<Button onClick={callSubmit}>
					Submit
				</Button>
			</Box>
		</>
	);
};