import React from "react";
import {
	Button,
	FormHelperText,
} from "@mui/material";
import PropTypes from "prop-types";
import { ButtonClickEvent } from "../../Types/browser_types";

interface YesNoControlProps {
	message: string | undefined,
	yesLabel?: string,
	onYes: (e: ButtonClickEvent) => void,
	noLabel?: string,
	onNo: (e: ButtonClickEvent) => void
};

export const YesNoControl = (props: YesNoControlProps) => {
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