import React from "react";
import {
	OutlinedInput,
	FormControl,
	InputLabel,
	FormHelperText } from "@mui/material";
import PropTypes from "prop-types";
import { useController } from "react-hook-form";


export function FormTextField(props) {
	const { name, label, formMethods, ...otherProps } = props;
	const { control } = formMethods;
	const labelId = `input-label-for-${name}`;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});

	const { ref, value, ...rest} = field;

	return (
		<FormControl>
			<InputLabel id={labelId}>{label}</InputLabel>
			<OutlinedInput
				{...rest}
				inputRef={ref}
				label={label}
				defaultValue={value}
				{...otherProps}
			/>
			{!!error && <FormHelperText error={!!error}>
				{error.message}
			</FormHelperText>}
		</FormControl>
	);
}

FormTextField.propTypes = {
	name: PropTypes.string.isRequired,
	formMethods: PropTypes.object,
	label: PropTypes.string,
};