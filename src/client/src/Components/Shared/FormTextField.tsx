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
	disabled?: boolean
};

export function FormTextField<FormT extends FieldValues>(
	props: FormTextFieldProps<FormT>
) {
	const { name, label, formMethods, ...otherProps } = props;
	const { control, register } = formMethods;

	const { fieldState: { error } }
		= useController({
			name,
			control,
		});

	const { ref, ...rest} = register(name);

	return (
		<TextField
			{...rest}
			inputRef={ref}
			label={label}
			defaultValue=""
			InputLabelProps={{ shrink: true }}
			error={!!error}
			helperText={error && error.message}
			variant="standard"
			{...otherProps}
		/>
	);
}