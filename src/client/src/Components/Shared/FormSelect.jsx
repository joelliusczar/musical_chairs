import React from "react";
import { Select, InputLabel, FormControl } from "@mui/material";
import PropTypes from "prop-types";
import { useController } from "react-hook-form";

export function FormSelect(props) {
	const { name, children, label, formMethods, ...otherProps } = props;
	const labelId = `input-label-for-${name}`;
	const { control } = formMethods;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});
	return (
		<FormControl>
			<InputLabel id={labelId}>{label}</InputLabel>
			<Select
				name={field.name}
				onChange={field.onChange}
				onBlur={field.onBlur}
				value={field.value}
				error={!!error}
				label={label}
				labelId={labelId}
				{...otherProps}
			>
				{children}
			</Select>
		</FormControl>
	);
}

FormSelect.propTypes = {
	name: PropTypes.string,
	label: PropTypes.string,
	children: PropTypes.any,
	formMethods: PropTypes.object,
};