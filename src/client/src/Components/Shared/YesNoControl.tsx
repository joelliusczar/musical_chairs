import React, { useState } from "react";
import {
	Button,
	FormHelperText,
	Box,
	Dialog,
} from "@mui/material";
import { ButtonClickEvent } from "../../Types/browser_types";

interface YesNoControlProps {
	message: string | undefined,
	yesLabel?: string,
	onYes: (e: ButtonClickEvent) => void,
	noLabel?: string,
	onNo: (e: ButtonClickEvent) => void
}

export const YesNoControl = (props: YesNoControlProps) => {
	const {message, yesLabel, onYes, noLabel, onNo} = props;
	return <>
		<FormHelperText>{message || ""}</FormHelperText>
		<Button onClick={onYes}>{yesLabel || "Yes"}</Button>
		<Button onClick={onNo}>{noLabel || "No"}</Button>
	</>;
};

interface YesNoControlModalProps extends YesNoControlProps {
	promptLabel: string,
}

export const YesNoModalOpener = (props: YesNoControlModalProps) => {

	const { onYes, onNo, promptLabel } = props;

	const [itemNewOpen, setItemNewOpen ] = useState(false);

	const _onNo = (e: ButtonClickEvent) => {
		setItemNewOpen(false);
		onNo && onNo(e);
	};

	const _onYes = (e: ButtonClickEvent) => {
		setItemNewOpen(false);
		onYes(e);
	};


	return (
		<>
			<Box>
				<Button onClick={() => setItemNewOpen(true)}>{promptLabel}</Button>
			</Box>
			<Dialog open={itemNewOpen} onClose={_onNo} scroll="body">
				<YesNoControl
					{...props}
					onYes={_onYes}
					onNo={_onNo}
				/>
			</Dialog>
		</>);
};
