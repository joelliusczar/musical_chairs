import {
	Table,
	TableBody,
	TableContainer,
	TableCell,
	TableHead,
	TableRow,
	Box,
	Typography,
	Button,
} from "@mui/material";
import React, { useEffect, useState, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { PrimitiveObject } from "../../Types/generic_types";

type OrderByFieldProps = {
	name: string,
	label: string,
	disabled?: boolean,
	getPageUrl: (
		params: PrimitiveObject,
		currentLocation: string,
		currentPathName: string,
	) => string,
};

export function OrderByField(props: OrderByFieldProps) {
	const { name, label, getPageUrl } = props;

	const navigate = useNavigate();
	const location = useLocation();

	const handleClick = () => {
		navigate(
			getPageUrl(
				{
					orderby: name,
					page: 1,
				},
				location.search,
				location.pathname
			),
			{ replace: true }
		);
	};

	return <TableCell
		onClick={handleClick}
	>
		{label}
	</TableCell>;
}