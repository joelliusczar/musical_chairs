import React from "react";
import { FormHelperText, Typography, Box } from "@mui/material";
import { FormSelect, FormSelectPropsSelected } from "../Shared/FormSelect";
import { FieldValues } from "react-hook-form";
import { PlaylistInfo } from "../../Types/playlist_types";


export const PlaylistSelect = <
	FormT extends FieldValues,
	Multiple extends boolean | undefined = false,
>(
		props: FormSelectPropsSelected<PlaylistInfo, FormT, Multiple>

	) => {

	return (
		<FormSelect
			renderOption={(renderProps, option) => {
				if (option) {
					const { className } = renderProps;
					return (
						<li
							{...renderProps}
							key={option.id}
							className={`app-form-select form-select ${className}`}
						>
							<Box className="form-select select-subtext">
								<Typography>{option.name}</Typography>
							</Box>
							<Box className="form-select select-subtext">
								<FormHelperText className="form-select select-subtext">
									Owner: {option.owner?.username}
								</FormHelperText>
							</Box>
						</li>
					);
				}
				return (
					<span {...renderProps}>
					</span>);
			}}
			{...props}
		/>
	);
};