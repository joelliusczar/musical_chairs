import React, {useState, useReducer, useEffect } from "react";
import { Box, Button, Dialog, MenuItem, Chip } from "@mui/material";
import { Cancel } from "@mui/icons-material";
import { TagNew } from "./TagNew";
import { FormikSelect } from "../Shared/FormikSelect";
import {
	waitingReducer,
	initialState,
	dispatches,
	waitingTypes,
} from "../Shared/waitingReducer";
import { fetchTags } from "./tagsService";
import Loader from "../Shared/Loader";
import { useField } from "formik";
import PropTypes from "prop-types";


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

const extraReducers = {
	[waitingTypes.add]: (state, payload) => {
		const items = [...state.data.items, payload]
			.sort((a,b) => a.name > b.name ? 1 : a.name < b.name ? -1 : 0);
		return {
			...state,
			data: {
				totalRows: state.data.totalRows + 1,
				items: items,
			},
		};
	},
};
export const TagAssignment = (props) => {
	const { name } = props;
	const [tagNewOpen, setTagNewOpen ] = useState(false);
	const [state, dispatch] = useReducer(
		waitingReducer(extraReducers),
		tagsInitialData
	);
	const { callStatus: callStatus } = state;

	const [ { value },,{ setValue, setTouched }] = useField(name);

	const closeModal = () => {
		setTagNewOpen(false);
	};

	const tagCreated = (tag) => {
		dispatch(dispatches.add(tag));
		closeModal();
	};

	const unassignTag = (e, idx) => {
		const items = [...value];
		items.splice(idx, 1);
		setValue(items);
		setTouched(true);
	};

	useEffect(() => {
		const fetch = async () => {
			try {
				if(!callStatus) {
					dispatch(dispatches.started());
					const data = await fetchTags();
					dispatch(dispatches.done(data));
				}
			}
			catch(err) {
				dispatch(dispatches.failed(err.response.data.detail[0].msg));
			}
		};

		fetch();
	}, [callStatus, dispatch]);

	return (
		<>
			<Box sx={inputField}>
				<Button onClick={() => setTagNewOpen(true)}>Add New Tag</Button>
			</Box>
			<Loader status={callStatus} error={state.error}>
				<Box sx={inputField}>
					<FormikSelect
						name={name}
						multiple
						sx={{ minWidth: 195 }}
						renderValue={(selected) => (
							<Box
								sx={{ display: "flex", flexWrap: "wrap", gap: .5}}
							>
								{selected.map((s, idx) => {
									return (
										<Chip
											key={`selectedTag_${idx}`}
											label={s.name}
											color="primary"
											clickable
											deleteIcon={
												<Cancel
													onMouseDown={(e) => e.stopPropagation()}
												/>
											}
											onDelete={(e) => unassignTag(e, idx)}
										/>
									);
								})}
							</Box>)}
					>
						<MenuItem key="tag_none" value=""></MenuItem>
						{state.data.items.map((t, idx) => {
							return (
								<MenuItem
									key={`tag_${idx}`}
									value={t}
								>
									{t.name}
								</MenuItem>
							);
						})}
					</FormikSelect>
				</Box>
			</Loader>
			<Dialog open={tagNewOpen} onClose={setTagNewOpen}>
				<TagNew afterSubmit={tagCreated} onCancel={closeModal} />
			</Dialog>
		</>
	);
};

TagAssignment.propTypes = {
	name: PropTypes.string,
};