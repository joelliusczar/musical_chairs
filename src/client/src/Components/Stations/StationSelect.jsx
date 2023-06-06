import React from "react";
import { Grid } from "@mui/material";
import { FormSelect } from "../Shared/FormSelect";

export const StationSelect = (props) => {

	return (
		<FormSelect
			renderGroup={(renderProps) => {
				return (<Grid container key={renderProps.key} >
					<Grid container item>
						<Grid item xs={6}>Station</Grid>
						<Grid item xs={6}>Owner</Grid>
					</Grid>
					<Grid container item>
						{renderProps.children}
					</Grid>
				</Grid>);
			}}
			groupBy={() => ""}
			renderOption={(renderProps, option) => {
				if (option) {
					return (
						<Grid container {...renderProps}>
							<Grid item xs={6}>{option.name}</Grid>
							<Grid item xs={6}>{option.owner?.username}</Grid>
						</Grid>
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