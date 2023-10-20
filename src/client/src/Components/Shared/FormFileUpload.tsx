import React from "react";
import { Button, FormHelperText } from "@mui/material";
import {
	useController,
	UseFormReturn,
	FieldValues,
	FieldPath,
} from "react-hook-form";

type FormFileUpload<FormT extends FieldValues> = {
	formMethods: UseFormReturn<FormT>
	name: FieldPath<FormT>
	label: string
	className?: string
	type?: string
	min?: string | number
	disabled?: boolean
};

export const FormFileUpload = <FormT extends FieldValues>(
	props: FormFileUpload<FormT>
) => {
	const { name, label, formMethods, ...otherProps } = props;
	const { control, register } = formMethods;

	const { fieldState: { error } }
		= useController({
			name,
			control,
		});


	return (
		<Button>
			<input
				{...register(name)}
				defaultValue=""
				{...otherProps}
				type="file"
			/>
			{error && <FormHelperText error={true}>
				{error?.message}
			</FormHelperText>}
		</Button>
	);
};