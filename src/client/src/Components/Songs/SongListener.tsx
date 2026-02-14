import React, { useState } from "react";
import { Button } from "@mui/material";

import { getDownloadAddress } from "../../Helpers/request_helpers";

type SongListenerProps = {
	audioId: string,
};

export const SongListener = (props: SongListenerProps) => {

	const { audioId } = props;
	const [dlUrl, setDlUrl] = useState("");

	const downloadSong = () => {
		const url = getDownloadAddress(audioId);
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

