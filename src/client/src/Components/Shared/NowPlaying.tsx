import React from "react";
import PropTypes from "prop-types";
import { Typography } from "@mui/material";
import { NowPlayingInfo } from "../../Types/song_info_types";

const formatNowPlaying = (nowPlaying: NowPlayingInfo | null) => {
	if(!nowPlaying) return "No song info available";
	const song = nowPlaying.name || "{No song name}";
	const album = nowPlaying.album || "{No album name}";
	const artist = nowPlaying.artist || "{No artist name}";
	const str = `Song: ${song} - ${album} - ${artist}`;
	return str;
};

type NowPlayingProps = {
	nowPlaying: NowPlayingInfo | null
};

export const NowPlaying = (props: NowPlayingProps) => {
	const { nowPlaying } = props;
	return (
		<Typography>
			{formatNowPlaying(nowPlaying)}
		</Typography>
	);
};

NowPlaying.propTypes = {
	nowPlaying: PropTypes.shape({
		name: PropTypes.string,
		album: PropTypes.string,
		artist: PropTypes.string,
	}),
};