import React from "react";
import { TextField } from "@mui/material";
import {
	useController,
	UseFormReturn,
	FieldValues,
	FieldPath,
} from "react-hook-form";

type FormTextFieldProps<FormT extends FieldValues> = {
	formMethods: UseFormReturn<FormT>
	name: FieldPath<FormT>
	label: string
	className?: string
	type?: string
	min?: string | number
	disabled?: boolean,
	sx?: object
	onKeyUp?: (e: React.KeyboardEvent<HTMLDivElement>) 
		=> void
	inputRef?: React.RefCallback<HTMLInputElement | undefined>
};

export const FormTextField = <FormT extends FieldValues>(
	props: FormTextFieldProps<FormT>
) => {
	const { name, label, formMethods, inputRef, ...otherProps } = props;
	const { control, register } = formMethods;

	const { fieldState: { error } }
		= useController({
			name,
			control,
		});

	const { ref, ...rest} = register(name);

	const combinedRefs = (el: HTMLInputElement) => {
		ref(el);
		inputRef && inputRef(el);
	};

	return (
		<TextField
			{...rest}
			inputRef={combinedRefs}
			label={label}
			defaultValue=""
			InputLabelProps={{ shrink: true }}
			error={!!error}
			helperText={error && error.message}
			variant="standard"
			{...otherProps}
		/>
	);
};