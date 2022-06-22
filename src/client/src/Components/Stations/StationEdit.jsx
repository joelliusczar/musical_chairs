import React, { useState, useReducer, useEffect } from "react";
import { Box, Typography, Button, Dialog, MenuItem } from "@mui/material";
import { FormikProvider, useFormik } from "formik";
import { FormikTextField } from "../Shared/FormikTextField";
import { TagNew } from "./TagNew";
import {
	waitingReducer,
	initialState,
	dispatches,
	waitingTypes,
} from "../Shared/waitingReducer";
import { fetchTags } from "./stations_slice";
import { FormikSelect } from "../Shared/FormikSelect";
import Loader from "../Shared/Loader";

const inputField = {
	margin: 2,
};

const tagsInitialData = {
	...initialState,
	data: {
		totalRows: 0,
		items: [],
	},
};

const tagsExtraReducers = {
	[waitingTypes.add]: (state, payload) => {
		const items = [...state.data.items, payload];
		return {
			...state,
			data: {
				totalRows: state.data.totalRows + 1,
				items: items,
			},
		};
	},
};

export const StationEdit = () => {
	const [tagNewOpen, setTagNewOpen ] = useState(false);
	const [tagsState, tagsDispatch] = useReducer(
		waitingReducer(tagsExtraReducers),
		tagsInitialData
	);
	const { callStatus: tagsCallStatus } = tagsState;
	const formik = useFormik({
		initialValues: {
			stationName: "",
			displayName: "",
			tags: [],
		},
	});

	const closeModal = () => {
		setTagNewOpen(false);
	};

	const tagAdded = (tag) => {
		tagsDispatch(dispatches.add(tag));
		closeModal();
	};

	useEffect(() => {
		const fetch = async () => {
			try {
				if(!tagsCallStatus) {
					tagsDispatch(dispatches.started());
					const data = await fetchTags();
					tagsDispatch(dispatches.done(data));
				}
			}
			catch(err) {
				tagsDispatch(dispatches.failed(err.response.data.detail[0].msg));
			}
		};

		fetch();
	}, [tagsCallStatus, tagsDispatch]);


	return (
		<FormikProvider value={formik}>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a station
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="stationName"
					label="Internal Name"
				/>
			</Box>
			<Box sx={inputField}>
				<FormikTextField
					name="displayName"
					label="Display Name"
				/>
			</Box>
			<Box sx={inputField}>
				<Button onClick={() => setTagNewOpen(true)}>Add New Tag</Button>
			</Box>
			<Loader status={tagsCallStatus} error={tagsState.error}>
				<Box sx={inputField}>
					<FormikSelect name="tags">
						<MenuItem key="tag_none" value=""></MenuItem>
						{tagsState.data.items.map((t, idx) => {
							return (
								<MenuItem
									key={`tag_${idx}`}
									value={t.id}
								>
									{t.name}
								</MenuItem>
							);
						})}
					</FormikSelect>
				</Box>
			</Loader>
			<Box sx={inputField} >
				<Button onClick={formik.submitForm}>
					Submit
				</Button>
			</Box>
			<Dialog open={tagNewOpen} onClose={setTagNewOpen}>
				<TagNew afterSubmit={tagAdded} onCancel={closeModal} />
			</Dialog>
		</FormikProvider>
	);
};