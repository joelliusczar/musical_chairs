import React, { useState } from "react";
import { Box, Typography, Button, Dialog } from "@mui/material";
import { FormTextField } from "../Shared/FormTextField";
import { FormFileUpload } from "../Shared/FormFileUpload";
import { useSnackbar } from "notistack";
import {
	checkSuffixes,
	uploadSong,
} from "../../API_Calls/songInfoCalls";
import { useForm } from "react-hook-form";
import { formatError } from "../../Helpers/error_formatter";
import * as Yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import {
	UploadInfo,
	SongTreeNodeInfo,
	MultiUploadInfo,
} from "../../Types/song_info_types";
import { SubmitButton } from "../Shared/SubmitButton";
import { 
	useKeyedVoidWaitingReducer,
	keyedVoidDispatches as dispatches,
} from "../../Reducers/keyedVoidWaitingReducer";
import { Loader } from "../Shared/Loader";
import get from "just-safe-get";



const inputField = {
	margin: 2,
};


const initialValues = {
	files: [],
};


const getSchema = (prefix: string) => Yup.lazy(values => {
	const requestObj = checkSuffixes({ 
		prefix,
		songSuffixes: values.files.map(
			(f: UploadInfo) => ({ path: f.suffix, id: 0})
		),
	});
	const usedPromise = requestObj.call();
	return Yup.object().shape({
		files: Yup.array().of(Yup.object().shape({
			suffix: Yup.string().required().test(
				"suffix",
				(value) => `${value.value} is already used`,
				async (value: string | undefined) => {
					if (!value) return true;
					const used = await usedPromise;
					return !(	value in used) || !used[value];
				}
			),
		})),
	});
});


type SongUploadProps = {
	onCancel?: (e: unknown) => void
	afterSubmit?: (s: SongTreeNodeInfo[]) => void,
	prefix: string,
};

export const SongUpload = (props: SongUploadProps) => {
	const { onCancel, prefix } = props;
	const { enqueueSnackbar } = useSnackbar();
	const [ uploadState, uploadDispatch] = useKeyedVoidWaitingReducer();

	const _afterSubmit = () => {
		reset({});
	};

	const afterSubmit = props.afterSubmit || _afterSubmit;


	const formMethods = useForm<MultiUploadInfo>({
		defaultValues: initialValues,
		resolver: yupResolver(getSchema(prefix)),
	});
	const { handleSubmit, reset, formState } = formMethods;
	const callSubmit = handleSubmit(async values => {
		let idx = 0;
		try {
			const results: SongTreeNodeInfo[] = [];
			for (; idx < values.files.length; idx++) {
				const requestObj = uploadSong({
					prefix: prefix,
					files: [values.files[idx].file],
					suffix: values.files[idx].suffix,
				});
				uploadDispatch(dispatches.started([idx]));
				const result = await requestObj.call();
				if (!!result) {
					results.push(result);
				}
				uploadDispatch(dispatches.done([idx]));
			}
			afterSubmit(results);
			enqueueSnackbar("Save successful", { variant: "success"});
		}
		catch(err) {
			const errMsg = formatError(err);
			enqueueSnackbar(errMsg, { variant: "error"});
			uploadDispatch(dispatches.failed([{ key: idx, msg: errMsg}]));
			console.error(err);
		}
	});

	const { watch } = formMethods;
	const files = watch("files");




	return (
		<>
			<Box sx={inputField}>
				<Typography variant="h1">
					Upload a file in {prefix}
				</Typography>
			</Box>
			{(!!files?.length) && files.map((f, idx) => {
				return <Box sx={inputField} key={`files.${idx}.suffix`}>
					<FormTextField
						name={`files.${idx}.suffix`}
						label="Name"
						formMethods={formMethods}
					/>
					<Loader
						status={get(uploadState, `${idx}.callStatus`)}
						error={get(uploadState, `${idx}.error`)}
					>
						<Typography>Done</Typography>
					</Loader>
				</Box>;
			})
			}
			<Box sx={inputField}>
				<FormFileUpload
					name="files"
					label="File"
					formMethods={formMethods}
					type="file"
					multiple
					transform={{
						output: (e) => {
							return {
								target: {
									name: e.target.name,
									value: e.target.value ? 
										[...e.target.value].map(f => ({ 
											file: f,
											suffix: f.name,
										}
										)) : [],
								},
							};
						},
					}}
				/>
			</Box>

			<Box sx={inputField} >
				<SubmitButton
					loading={formState.isSubmitting}
					onClick={callSubmit}
					disabled={(files?.length || 0) < 1}
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


type SongUploadNewModalOpenerProps = {
	add?: (s: SongTreeNodeInfo[]) => void;
	prefix: string
}


export const SongUploadNewModalOpener = (
	props: SongUploadNewModalOpenerProps
) => {

	const { add, prefix } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const closeModal = () => {
		setItemNewOpen(false);
	};

	const itemCreated = (items: SongTreeNodeInfo[]) => {
		add && add(items);
		closeModal();
	};

	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>Upload new song</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={closeModal} scroll="body">
				<SongUpload
					afterSubmit={itemCreated}
					onCancel={closeModal}
					prefix={prefix}
				/>
			</Dialog>
		</>);
};


