import React from "react";
import { Select, InputLabel } from "@mui/material";
import { useField } from "formik";
import PropTypes from "prop-types";

export function FormikSelect(props) {
	const { name, children, label, ...otherProps } = props;
	const [ field, { error, touched } ] = useField(name);
	const showError = touched && !!error;
	const labelId = `input-label-for-${name}`;
	return (
		<>
			<InputLabel id={labelId}>{label}</InputLabel>
			<Select
				{...field}
				name={name}
				error={showError}
				label={label}
				labelId={labelId}
				{...otherProps}
			>
				{children}
			</Select>
		</>
	);
}

FormikSelect.propTypes = {
	name: PropTypes.string,
	label: PropTypes.string,
	children: PropTypes.any,

};