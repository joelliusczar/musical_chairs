import { TrackListing } from "../Types/song_info_types";

export const guessTrackNumber = (
	songInfo: TrackListing
) => {
	if (songInfo.tracknum > 0) return songInfo.tracknum;
	let guess = Number(songInfo.track);
	if (!isNaN(guess)) return guess;
	if (!songInfo.track) return 0;
	let re = /(\d+)([a-zA-Z])([a-zA-Z]*)/;
	let match = songInfo.track.match(re);
	if (match) {
		guess = Number(match[1]);
		guess += (
			(match[2].toLowerCase().charCodeAt(0) - "a".charCodeAt(0) + 1) / 10
		);
		if (match[3]) {
			guess += (
				(match[3].toLowerCase().charCodeAt(0) - "a".charCodeAt(0) + 1) / 100
			);
		}
		return guess;
	}
	re = /\D(\d+)-(\d+)/;
	match = songInfo.track.match(re);
	if (match) {
		guess = Number(match[1] + match[2]);
		return guess;
	}
	return 0;
};