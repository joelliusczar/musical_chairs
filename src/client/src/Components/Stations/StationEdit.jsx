import React, { useReducer, useEffect } from "react";
import { Box, Typography, Button } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import { TagAssignment } from "../Tags/TagAssignment";
import { saveStation, fetchStationForEdit } from "./stationService";
import { useSnackbar } from "notistack";
import { useHistory, useLocation } from "react-router-dom";
import { DomRoutes } from "../../constants";
import {
	waitingReducer,
	initialState,
	dispatches,
} from "../Shared/waitingReducer";

const inputField = {
	margin: 2,
};


export const StationEdit = () => {
	const { enqueueSnackbar } = useSnackbar();
	const urlHistory = useHistory();
	const [state, dispatch] = useReducer(waitingReducer(), initialState);
	const { callStatus } = state;
	const location = useLocation();
	const queryObj = new URLSearchParams(location.search);
	const id = queryObj.get("id");
	const stationName = queryObj.get("name");

	const formik = useFormik({
		initialValues: {
			name: "",
			displayName: "",
			tags: [],
		},
		onSubmit: async (values, { resetForm }) => {
			try {
				const stationId = id ? id : values.id ? values.id : null;
				const data = await saveStation({ values, id: stationId });
				resetForm({values: data});
				dispatch(dispatches.done());
				urlHistory.replace(getPageUrl({ id: data.id }));
				enqueueSnackbar("Save successful", { variant: "success"});
			}
			catch(err) {
				enqueueSnackbar(err.response.data.detail[0].msg, { variant: "error"});
			}
		},
	});
	const { resetForm } = formik;

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
				if(!callStatus && (id || stationName)) {
					dispatch(dispatches.started());
					const data = await fetchStationForEdit({
						params: {
							id,
							name: stationName,
						},
					});
					resetForm({values: data});
					dispatch(dispatches.done());
				}
			}
			catch(err) {
				dispatch(dispatches.failed(err.response.data.detail[0].msg));
			}
		};

		fetch();
	}, [dispatch, callStatus, id, stationName]);


	return (
		<FormikProvider value={formik}>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a station
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="name"
					label="Internal Name"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="displayName"
					label="Display Name"
				/>
			</Box>
			<TagAssignment name="tags" />
			<Box sx={inputField} >
				<Button onClick={formik.submitForm}>
					Submit
				</Button>
			</Box>
		</FormikProvider>
	);
};