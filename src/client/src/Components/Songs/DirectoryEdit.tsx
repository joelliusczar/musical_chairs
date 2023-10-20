import React, { useState, useEffect } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import {
	checkValues,
	saveDirectory,
} from "../../API_Calls/songInfoCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import {
	DirectoryInfo,
	SongTreeNodeInfo,
} from "../../Types/song_info_types";



const inputField = {
	margin: 2,
};


const initialValues = {
	suffix: "",
	prefix: "",
};



const validatePhraseIsUnused = async (
	value: string | undefined,
	context: Yup.TestContext<Partial<DirectoryInfo>>
) => {
	const id = context?.parent?.id;
	if (!value) return true;
	const used = await checkValues({ id, values: {
		"suffix": value,
		"prefix": context?.parent?.prefix,
	}});
	return !(context.path in used) || !used[context.path];
};

const schema = Yup.object().shape({
	suffix: Yup.string().required().test(
		"suffix",
		(value) => `${value.path} is already used`,
		validatePhraseIsUnused
	),
});


type DirectoryEditProps = {
	onCancel?: (e: unknown) => void
	afterSubmit?: (s: SongTreeNodeInfo) => void,
	prefix: string,
};

export const DirectoryEdit = (props: DirectoryEditProps) => {
	const { onCancel, prefix } = props;
	const { enqueueSnackbar } = useSnackbar();


	const _afterSubmit = () => {
		reset({});
	};

	const afterSubmit = props.afterSubmit || _afterSubmit;


	const formMethods = useForm<DirectoryInfo>({
		defaultValues: initialValues,
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			const result = await saveDirectory(values);
			afterSubmit(result);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			enqueueSnackbar(formatError(err), { variant: "error"});
			console.error(err);
		}
	});

	const setValue = formMethods.setValue;

	useEffect(() => {
		setValue("prefix", prefix);
	},[prefix, setValue]);


	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Create a directory in {prefix}
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="suffix"
					label="Name"
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
		</>
	);
};


type DirectoryNewModalOpenerProps = {
	add?: (s: SongTreeNodeInfo) => void;
	prefix: string
}


export const DirectoryNewModalOpener = (
	props: DirectoryNewModalOpenerProps
) => {

	const { add, prefix } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (item: SongTreeNodeInfo) => {
		add && add(item);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Add New Directory</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<DirectoryEdit
					afterSubmit={itemCreated}
					onCancel={closeModal}
					prefix={prefix}
				/>
			</Dialog>
		</>);
};


