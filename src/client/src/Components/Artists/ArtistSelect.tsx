import React from "react";
import { Box, Typography, FormHelperText } from "@mui/material";
import { FormSelect, FormSelectPropsSelected } from "../Shared/FormSelect";
import { FieldValues } from "react-hook-form";
import { ArtistInfo } from "../../Types/song_info_types";




export const ArtistSelect = <
	FormT extends FieldValues,
	Multiple extends boolean | undefined = false,
>(props: FormSelectPropsSelected<
		ArtistInfo,
		FormT,
		Multiple
	>
	) => {

	return (
		<FormSelect
			renderOption={(renderProps, option) => {
				if (option) {
					const { className } = renderProps;
					return (
						<li
							{...renderProps}
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