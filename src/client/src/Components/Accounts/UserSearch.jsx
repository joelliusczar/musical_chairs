import React, { useEffect, useState } from "react";
import {
	Autocomplete,
	Box,
	Button,
	Dialog,
	TextField,
	Typography,
} from "@mui/material";
import { searchUsers } from "../../API_Calls/userCalls";
import debouncePromise from "debounce-promise";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import { UserRoleDef } from "../../constants";
import { FormSelect } from "../Shared/FormSelect";

const inputField = {
	margin: 2,
};



export const UserSearch = (props) => {

	const { onCancel, formMethods } = props;

	const [options, setOptions] = useState([]);
	const [inputValue, setInputValue] = useState("");
	const { enqueueSnackbar } = useSnackbar();

	const stationRoles = Object.keys(UserRoleDef)
		.filter(k => k.startsWith("STATION"))
		.map(k => UserRoleDef[k]);

	const handleInputChange = (e, newValue) => {
		setInputValue(newValue);
	};

	useEffect(() => {
		if (!inputValue) {
			return;
		}
		const searchCall = debouncePromise(async (searchTerm) => {
			try {
				const data = await searchUsers({ params: {searchTerm} });
				setOptions(data);
			}
			catch(err) {
				enqueueSnackbar(formatError(err), { variant: "error"});
				console.error(err);
			}
		},100);

		searchCall(inputValue);
	},[inputValue, enqueueSnackbar]);

	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Add an artist
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormSelect
					options={options}
					getOptionLabel={(option) => option ? option.username : ""}
					filterOptions={(x) => x}
					inputValue={inputValue}
					onInputChange={handleInputChange}
					freeSolo
					label="Assign Users"
					formMethods={formMethods}
				/>
			</Box>
			<Box sx={inputField} >
				<Button onClick={() => {}}>
					Submit
				</Button>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</>
	);
};

UserSearch.propTypes = {
	onCancel: PropTypes.func,
	formMethods: PropTypes.object,
};

export const UserSearchModalOpener = () => {


	const [userSearchOpen, setUserSearchOpen ] = useState(false);

	const closeModal = () => {
		setUserSearchOpen(false);
	};


	return (
		<>
			<Box>
				<Button onClick={() => setUserSearchOpen(true)}>
					Assign Users
				</Button>
			</Box>
			<Dialog open={userSearchOpen} onClose={closeModal} scroll="body">
				<UserSearch />
			</Dialog>
		</>);
};
