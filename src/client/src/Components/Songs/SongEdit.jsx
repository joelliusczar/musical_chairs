import React, { useReducer } from "react";
import { Box, Typography, Button } from "@mui/material";
import {
	useAlbumData,
} from "../../Context_Providers/AppContextProvider";

const inputField = {
	margin: 2,
};

export const SongEdit = () => {
	const { items, map, callStatus } = useAlbumData();

	return (<>
		<Box sx={inputField}>
			<Typography variant="h1">
				Edit a song
			</Typography>
		</Box>
	</>);
};