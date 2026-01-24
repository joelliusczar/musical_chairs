import React, { useCallback, useState, useEffect } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { useSnackbar } from "notistack";
import {
	Calls,
} from "../../API_Calls/songInfoCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import {
	DirectoryInfo,
	SongTreeNodeInfo,
} from "../../Types/song_info_types";
import { SubmitButton } from "../Shared/SubmitButton";
import { ListData } from "../../Types/pageable_types";
import { Dictionary } from "../../Types/generic_types";
import { extract_parent } from "../../Helpers/string_helpers";



const inputField = {
	margin: 2,
};


const initialValues = {
	suffix: "",
	prefix: "",
};


export const ActionTypes = {
	ADD: "add" as const,
	RENAME: "rename" as const,
} as const;


const validatePhraseIsUnused = async (
	value: string | undefined,
	context: Yup.TestContext<Partial<DirectoryInfo>>
) => {
	const id = context?.parent?.id;
	if (!value) return true;
	const requestObj = Calls.checkValues({ id, values: {
		"suffix": value,
		"prefix": context?.parent?.prefix,
	}});
	const used = await requestObj.call();
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
	afterSubmit?: (
		treeUpdates: Dictionary<ListData<SongTreeNodeInfo>>,
		prefix: string,
		suffic: string,
	) => void,
	prefix: string,
	action: typeof ActionTypes.ADD | typeof ActionTypes.RENAME
};

export const DirectoryEdit = (props: DirectoryEditProps) => {
	const { onCancel, prefix, action } = props;
	const { enqueueSnackbar } = useSnackbar();



	const _afterSubmit = () => {
		reset({});
	};

	const setRef = useCallback((el: HTMLInputElement) => {
		if (el) {
			el.focus();
		}
	},[]);

	const afterSubmit = props.afterSubmit || _afterSubmit;


	const formMethods = useForm<DirectoryInfo>({
		defaultValues: initialValues,
		resolver: yupResolver(schema),
	});
	const { handleSubmit, reset, formState } = formMethods;
	const callSubmit = handleSubmit(async values => {
		try {
			if (action === ActionTypes.ADD ) {
				const requestObj = Calls.saveDirectory(values);
				const result = await requestObj.call();
				afterSubmit(result, values.prefix, values.suffix);
			}
			else {
				const requestObj = Calls.renameDirectory(values);
				const result = await requestObj.call();
				afterSubmit(
					result,
					extract_parent(values.prefix),
					values.suffix
				);
			}
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
					{
						action === ActionTypes.ADD
							? `Create a directory in ${prefix}`
							: `Rename ${prefix}`
					}
					
				</Typography>
			</Box>
			<Box sx={inputField}>
				<FormTextField
					name="suffix"
					label="Name"
					formMethods={formMethods}
					onKeyUp={e => {
						if (e.code === "Enter") {
							callSubmit(e);
						}
					}}
					inputRef={setRef}
				/>
			</Box>

			<Box sx={inputField} >
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
				>
					Submit
				</SubmitButton>
				{onCancel &&<Button onClick={onCancel}>
						Cancel
				</Button>}
			</Box>
		</>
	);
};


type DirectoryNewModalOpenerProps = {
	add?: (
		treeUpdates: Dictionary<ListData<SongTreeNodeInfo>>,
		prefix: string,
		suffix: string
	) => void;
	prefix: string,
	action?: "add" | "rename"
}


export const DirectoryNewModalOpener = (
	props: DirectoryNewModalOpenerProps
) => {

	const { add, prefix, action = ActionTypes.ADD } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (
		item: Dictionary<ListData<SongTreeNodeInfo>>,
		prefix: string,
		suffix: string
	) => {
		add && add(item, prefix, suffix);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>
					{action === ActionTypes.ADD
						? "Add New Directory"
						: "Rename Directory"
					}
				</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<DirectoryEdit
					afterSubmit={itemCreated}
					onCancel={closeModal}
					prefix={prefix}
					action={action}
				/>
			</Dialog>
		</>);
};


