import React from "react";
import { Typography } from "@mui/material";
import { SongListDisplayItem } from "../../Types/song_info_types";

const formatNowPlaying = (nowPlaying: SongListDisplayItem | null) => {
	if(!nowPlaying) return "No song info available";
	const song = nowPlaying.name || "{No song name}";
	const album = nowPlaying.album || "{No album name}";
	const artist = nowPlaying.artist || "{No artist name}";
	const str = `Song: ${song} - ${album} - ${artist}`;
	return str;
};

type NowPlayingProps = {
	nowPlaying: SongListDisplayItem | null
};

export const NowPlaying = (props: NowPlayingProps) => {
	const { nowPlaying } = props;
	return (
		<Typography>
			{formatNowPlaying(nowPlaying)}
		</Typography>
	);
};
