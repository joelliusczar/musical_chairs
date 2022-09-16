import React from "react";
import { Select, InputLabel, FormControl } from "@mui/material";
import PropTypes from "prop-types";
import { useController } from "react-hook-form";

const defaultTransform = {
	input: (value) => value,
	output: (e) => e,
};

export function FormSelect(props) {
	const {
		name,
		children,
		label,
		formMethods,
		transform,
		...otherProps
	} = props;
	const labelId = `input-label-for-${name}`;
	const { control } = formMethods;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});

	const _transform = {...defaultTransform, ...(transform || {})};

	return (
		<FormControl>
			<InputLabel id={labelId}>{label}</InputLabel>
			<Select
				id={field.name}
				name={field.name}
				onChange={_transform.output(field.onChange)}
				onBlur={field.onBlur}
				value={_transform.input(field.value)}
				error={!!error}
				label={label}
				labelId={labelId}
				variant="standard"
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
	transform: PropTypes.shape({
		input: PropTypes.func,
		output: PropTypes.func,
	}),
};