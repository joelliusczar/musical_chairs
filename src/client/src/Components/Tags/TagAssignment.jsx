import React, { useState, useEffect } from "react";
import { Box, Button, Dialog, MenuItem, Chip } from "@mui/material";
import { Cancel } from "@mui/icons-material";
import { TagNew } from "./TagNew";
import { FormSelect } from "../Shared/FormSelect";
import Loader from "../Shared/Loader";
import PropTypes from "prop-types";
import { useTagData } from "../../Context_Providers/AppContextProvider";


const inputField = {
	margin: 2,
};


export const TagAssignment = (props) => {
	const { name, formMethods } = props;

	const { items, callStatus, error, add } = useTagData();
	const { setValue, getValues } = formMethods;
	const [tagNewOpen, setTagNewOpen ] = useState(false);



	const closeModal = () => {
		setTagNewOpen(false);
	};

	const tagCreated = (tag) => {
		add(tag);
		closeModal();
	};

	const unassignTag = (_e, idx) => {
		const value = getValues(name);
		console.log(value);
		const items = [...value];
		items.splice(idx, 1);
		setValue(name, items);
	};

	// useEffect(() => {
	// 	const map = items.reduce((soFar, x) => soFar.set(x.id, x), new Map());
	// 	const tracked = 
	// },[items]);

	return (
		<>
			<Box sx={inputField}>
				<Button onClick={() => setTagNewOpen(true)}>Add New Tag</Button>
			</Box>
			<Loader status={callStatus} error={error}>
				<Box sx={inputField}>
					<FormSelect
						name={name}
						formMethods={formMethods}
						label="Tags"
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
						{items.map((t, idx) => {
							return (
								<MenuItem
									key={`tag_${idx}`}
									value={t}
								>
									{t.name}
								</MenuItem>
							);
						})}
					</FormSelect>
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
	formMethods: PropTypes.object,
};