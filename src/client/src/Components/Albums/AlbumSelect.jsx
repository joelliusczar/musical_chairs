import React from "react";
import { FormHelperText, Typography, Box } from "@mui/material";
import { FormSelect } from "../Shared/FormSelect";

export const AlbumSelect = (props) => {

	return (
		<FormSelect
			renderOption={(renderProps, option) => {
				if (option) {
					const { className } = renderProps;
					return (
						<Box
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
						</Box>
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