import React, { useState } from "react";
import { Button } from "@mui/material";

import {
	songDownloadUrl,
} from "../../API_Calls/songInfoCalls";

type SongListenerProps = {
	audioId: number,
};

export const SongListener = (props: SongListenerProps) => {

	const { audioId } = props;
	const [dlUrl, setDlUrl] = useState("");

	const downloadSong = async () => {
		const requestObj = songDownloadUrl({id : audioId});
		const url = await requestObj.call();
		setDlUrl(url);
	};

	return (
		<>
			{!dlUrl ? <Button
				onClick={downloadSong}
			>
				Download song
			</Button>
				:
				<audio controls src={dlUrl}></audio>
			}
		</>
	);
};

