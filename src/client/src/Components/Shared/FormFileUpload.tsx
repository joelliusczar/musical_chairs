import React, { useState } from "react";
import { Button, FormHelperText } from "@mui/material";
import {
	useController,
	UseFormReturn,
	FieldValues,
	FieldPath,
} from "react-hook-form";
import {
	FileListEvent,
	CustomFileAttachEvent,
} from "../../Types/browser_types";
import { css } from "@emotion/react";

type TransformType<
T extends File | { file: File } = File,
U = T extends File ? File : { file: File }
> = {
	input: (value: U[]) => U[],
	output: (e: FileListEvent) => CustomFileAttachEvent
};

const defaultTransformFactory = <
T extends File | { file: File } = File,
U = T extends File ? File : { file: File }
>
	(): TransformType<T, U> => ({
		input: (value) => value,
		output: (e) => ({
			target: {
				name: e.target.name,
				value: e.target.value ?
					[...e.target.value].map(f => ({ file: f })) : [],
			},
		}),
	});

type FormFileUpload
<
	FormT extends FieldValues,
	T extends File | { file: File } = File
> = {
	formMethods: UseFormReturn<FormT>
	name: FieldPath<FormT>
	label: string
	className?: string
	type?: string
	min?: string | number
	disabled?: boolean,
	multiple?: boolean,
	transform?: Partial<TransformType<T>
>
};

export const FormFileUpload = <
	FormT extends FieldValues,
	T extends File | { file: File } = File
>(
		props: FormFileUpload<FormT, T>
	) => {
	const { name, formMethods, transform, ...otherProps } = props;
	const { control } = formMethods;
	const [over, setOver] = useState(false);

	const styles = {
		fileUpload: css`
			background-color: ${over ? "hsl(150 100% 30% / .1)": "inherit"}
		`,
	};

	const { fieldState: { error }, field }
		= useController({
			name,
			control,
		});

	const _transform = {
		...defaultTransformFactory<T>(),
		...(transform || {}),
	};

	return (
		<Button  css={styles.fileUpload}>
			<input
				id={field.name}
				name={field.name}
				defaultValue=""
				onChange={(e) => {
					field.onChange(_transform.output({
						target: { name: field.name, value: e.target.files} ,
					}));
				}}
				onBlur={field.onBlur}
				// value={_transform.input(field.value)}
				type="file"
				onDragEnter={() => setOver(true)}
				onDragLeave={() => setOver(false)}
				onDrop={() => setOver(false)}
				{...otherProps}
			/>
			{error && <FormHelperText error={true}>
				{error?.message}
			</FormHelperText>}
		</Button>
	);
};