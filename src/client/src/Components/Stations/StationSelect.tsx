import React from "react";
import { Box, Typography, FormHelperText } from "@mui/material";
import { FormSelect, FormSelectPropsDefault } from "../Shared/FormSelect";
import { StationInfo } from "../../Types/station_types";
import { FieldValues } from "react-hook-form";

export const StationSelect = <FormT extends FieldValues>(
	props: FormSelectPropsDefault<StationInfo, FormT>
) => {

	return (
		<FormSelect<StationInfo, FormT>
			renderOption={(renderProps: any, option) => {
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