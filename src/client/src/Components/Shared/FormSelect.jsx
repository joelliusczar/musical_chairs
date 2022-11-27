import React from "react";
import {
	Autocomplete,
	TextField,
	FormHelperText,
} from "@mui/material";
import PropTypes from "prop-types";
import { useController } from "react-hook-form";

const defaultTransform = {
	input: (value) => value,
	output: (e) => e,
};

export function FormSelect(props) {
	const {
		name,
		options,
		label,
		formMethods,
		transform,
		...otherProps
	} = props;
	const { control } = formMethods;

	const { field, fieldState: { error } }
		= useController({
			name,
			control,
		});

	const _transform = {...defaultTransform, ...(transform || {})};

	return (
		<>
			<Autocomplete
				options={options}
				getOptionLabel={(option) => option ? option.name : ""}
				name={field.name}
				onChange={(e, value) => field.onChange(_transform.output({
					target: { name: field.name, value: value},
				}))}
				onBlur={field.onBlur}
				value={_transform.input(field.value)}
				renderInput={(params) => {
					return <TextField
						{...params}
						label={label}
						variant="standard"
					/>;
				}}
				{...otherProps}
			/>
			{error && <FormHelperText error={true}>
				{error?.message}
			</FormHelperText>}
		</>
	);
}

FormSelect.propTypes = {
	name: PropTypes.string,
	label: PropTypes.string,
	formMethods: PropTypes.object,
	options: PropTypes.arrayOf(PropTypes.shape({
		id: PropTypes.number,
		name: PropTypes.string,
	})),
	transform: PropTypes.shape({
		input: PropTypes.func,
		output: PropTypes.func,
	}),
	disabled: PropTypes.bool,
};