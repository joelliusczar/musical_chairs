import React from "react";
import { TextField } from "@mui/material";
import PropTypes from "prop-types";
import { useController } from "react-hook-form";


export function FormTextField(props) {
	const { name, label, formMethods, ...otherProps } = props;
	const { control, register } = formMethods;

	const { fieldState: { error } }
		= useController({
			name,
			control,
		});

	const { ref, ...rest} = register(name);

	console.log(error);

	return (
		<TextField
			{...rest}
			inputRef={ref}
			label={label}
			defaultValue=""
			{...otherProps}
			InputLabelProps={{ shrink: true }}
			error={!!error}
			helperText={error && error.message}
			variant="standard"
		/>
	);
}

FormTextField.propTypes = {
	name: PropTypes.string.isRequired,
	formMethods: PropTypes.object,
	label: PropTypes.string,
};