import React, { useEffect, useState, useRef } from "react";
import {
	Box,
	Button,
	Dialog,
	Typography,
} from "@mui/material";
import { searchUsers } from "../../API_Calls/userCalls";
import debouncePromise from "debounce-promise";
import PropTypes from "prop-types";
import { useSnackbar } from "notistack";
import { formatError } from "../../Helpers/error_formatter";
import { FormSelect } from "../Shared/FormSelect";
import { useForm, UseFormReturn } from "react-hook-form";
import { User } from "../../Types/user_types";
import { ClickEvent, ChangeEvent } from "../../Types/browser_types";

type UserSeachInitialValues = {
	selectedUser: User | null
}

type UserSearchProps = {
	formMethods: UseFormReturn<UserSeachInitialValues>
	onCancel?: (e: ClickEvent) => void
	onConfirm: (e: ClickEvent) => void
}

const inputField = {
	margin: 2,
};


export const UserSearch = (
	props: UserSearchProps
) => {

	const { onCancel, formMethods, onConfirm } = props;
	const searchCache = useRef<{[term: string]: User[]}>({});

	const [options, setOptions] = useState<User[]>([]);
	const [inputValue, setInputValue] = useState("");
	const { enqueueSnackbar } = useSnackbar();

	const handleInputChange = (e: ChangeEvent, newValue: string) => {
		setInputValue(newValue);
	};

	useEffect(() => {
		if (!inputValue) {
			return;
		}
		const searchCall = debouncePromise(async (searchTerm: string) => {
			try {
				if (searchTerm in searchCache.current) {
					setOptions(searchCache.current[searchTerm]);
					return;
				}
				const data = await searchUsers({ params: {searchTerm} });
				searchCache.current[searchTerm] = data;
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
					Assign a user
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormSelect<User, UserSeachInitialValues>
					name="selectedUser"
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
				<Button onClick={onConfirm}>
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
	onConfirm: PropTypes.func.isRequired,
	onCancel: PropTypes.func,
	formMethods: PropTypes.object.isRequired,
};

type UserSearchModalOpenerProps = {
	onConfirm: (selected: User | null) => void
}

export const UserSearchModalOpener = (props: UserSearchModalOpenerProps) => {

	const { onConfirm } = props;

	const [userSearchOpen, setUserSearchOpen ] = useState(false);

	const formMethods = useForm<UserSeachInitialValues>({
		defaultValues: { selectedUser: null },
	});



	const closeModal = () => {
		reset({ selectedUser: null });
		setUserSearchOpen(false);
	};

	const { handleSubmit, reset } = formMethods;
	const callSubmit = handleSubmit(values => {
		onConfirm(values.selectedUser);
		reset({ selectedUser: null });
		closeModal();
	});

	return (
		<>
			<Box>
				<Button onClick={() => setUserSearchOpen(true)}>
					Assign Users
				</Button>
			</Box>
			<Dialog open={userSearchOpen} onClose={closeModal} scroll="body">
				<UserSearch
					formMethods={formMethods}
					onConfirm={callSubmit}
				/>
			</Dialog>
		</>);
};


UserSearchModalOpener.propTypes = {
	onConfirm: PropTypes.func.isRequired,
};