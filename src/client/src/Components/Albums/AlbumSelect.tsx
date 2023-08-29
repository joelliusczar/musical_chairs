import React from "react";
import { FormHelperText, Typography, Box } from "@mui/material";
import { FormSelect, FormSelectPropsSelected } from "../Shared/FormSelect";
import { FieldValues } from "react-hook-form";
import { AlbumInfo } from "../../Types/song_info_types";

export const AlbumSelect = <FormT extends FieldValues>(
	props: FormSelectPropsSelected<AlbumInfo, FormT>
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
									Artist: {option.albumArtist?.name ?
										option.albumArtist?.name: ""}
								</FormHelperText>
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