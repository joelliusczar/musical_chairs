import React, { useRef, useEffect } from "react";
import { TextField } from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import { PrimitiveObject } from "../../Types/generic_types";

type SearchTextFieldProps = {
	name: string,
	className?: string
	type?: string
	min?: string | number
	disabled?: boolean,
	defaultValue?: string,
	getPageUrl: (
		params: PrimitiveObject,
		currentLocation: string,
		currentPathName: string,
	) => string,
};

export function SearchTextField(
	props: SearchTextFieldProps
) {
	const {
		name,
		getPageUrl,
		...otherProps
	} = props;

	const navigate = useNavigate();
	const location = useLocation();

	const fieldRef = useRef<HTMLInputElement | null>();

	useEffect(() => {
		const queryObj = new URLSearchParams(location.search);
		if (fieldRef.current) {
			fieldRef.current.value = queryObj.get(name) || "";
		}

	},[location.search, name]);

	const handleSearch = (key: string, value: string) => {
		navigate(
			getPageUrl(
				{
					[key]: value,
					page: 1,
				},
				location.search,
				location.pathname
			),
			{ replace: true }
		);
	};

	return (
		<TextField
			name={name}
			inputRef={fieldRef}
			size="small"
			InputLabelProps={{ shrink: true }}
			onBlur={(e) => {
				handleSearch(e.target.name, e.target.value);
			}}
			{...otherProps}
		/>
	);
}