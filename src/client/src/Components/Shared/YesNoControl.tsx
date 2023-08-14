import React from "react";
import {
	Button,
	FormHelperText,
} from "@mui/material";
import PropTypes from "prop-types";

export const YesNoControl = (props) => {
	const {message, yesLabel, onYes, noLabel, onNo} = props;
	return <>
		<FormHelperText>{message || ""}</FormHelperText>
		<Button onClick={onYes}>{yesLabel || "Yes"}</Button>
		<Button onClick={onNo}>{noLabel || "No"}</Button>
	</>;
};

YesNoControl.propTypes = {
	message: PropTypes.string,
	yesLabel: PropTypes.string,
	onYes: PropTypes.func.isRequired,
	noLabel: PropTypes.string,
	onNo: PropTypes.func.isRequired,
};