import React from "react";
import { TextField } from "@mui/material";
import { useField } from "formik";
import PropTypes from "prop-types";


export function FormikTextField(props) {
	const { name, ...otherProps } = props;
	const [ field, { error, touched } ] = useField(name);
	const showError = touched && !!error;
	return (<TextField
		{...field}
		name={name}
		error={showError}
		helperText={showError ? error : null}
		{...otherProps}
	/>);
}

FormikTextField.propTypes = {
	name: PropTypes.string,
	required: PropTypes.bool,
};