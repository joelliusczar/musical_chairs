import React from "react";
import {
	Button,
	ButtonProps,
} from "@mui/material";
import { Loader } from "./Loader";
import { CallStatus } from "../../constants";

type SubmitButtonProps = {
	loading: boolean,
} & ButtonProps;

export const SubmitButton = (props: SubmitButtonProps) => {
	const { loading, ...otherProps } = props;
	const status = loading ? CallStatus.loading : CallStatus.done;
	return <Loader status={status} error={null}>
		<Button {...otherProps}/>
	</Loader>;
};