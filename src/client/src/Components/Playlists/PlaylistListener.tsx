import React, { 
	useEffect,
	useRef,
} from "react";
import { Button } from "@mui/material";
import { SongListDisplayItem } from "../../Types/song_info_types";
import { getDownloadAddress } from "../../Helpers/request_helpers";
import { IdValue } from "../../Types/generic_types";

type PlaylistListenerProps = {
	audioItems: SongListDisplayItem[],
	nextUp: SongListDisplayItem | null,
	queueNext: (steps: number) => void,
	parentId: IdValue,
};

const getAudioElement = (className: string) => {
	const audioSelection = 
			document.getElementsByClassName(className);
	if (audioSelection.length) {
		const audioElement = audioSelection[0] as HTMLAudioElement;
		return audioElement;
	}
	return null;
};


export const PlaylistListener = (props: PlaylistListenerProps) => {

	const { nextUp, queueNext, parentId } = props;

	const timeDisplayCtl = useRef<HTMLSpanElement>(null);
	const playButtonCtl = useRef<HTMLButtonElement>(null);


	const formatTime = (seconds: number) => {
		const minutes = Math.floor(seconds / 60);
		const wholeSeconds = Math.floor(seconds - (minutes * 60));
		return `${minutes}:${String(wholeSeconds).padStart(2,"0")}`;
	};

	const songEnd = () => {
		const previousAudio = getAudioElement("previous-audio");
		if (previousAudio) {
			const audioParent = 
					document.getElementById(`playlist-listener-${parentId}`);
			if (audioParent) {
				audioParent.removeChild(previousAudio);
			}
		}
		const currentAudio = getAudioElement("current-audio");
		if (currentAudio) {
			currentAudio.classList.remove("current-audio");
			currentAudio.classList.add("previous-audio");
		}
		const nextAudio = getAudioElement("next-audio");
		if (nextAudio) {
			nextAudio.classList.remove("next-audio");
			nextAudio.classList.add("current-audio");
			nextAudio.play();
		}
	};
	

	const timeUpdate = () => {
		const currentAudio = getAudioElement("current-audio");
		if (currentAudio) {
			const currentTime = currentAudio.currentTime;
			const duration = currentAudio.duration;
			if (timeDisplayCtl.current) {
				const timeDisplay = 
					`${formatTime(currentTime)}/${formatTime(duration)}`;
				timeDisplayCtl.current.innerText = timeDisplay;
			}

			if (duration < 30 || (currentTime / duration) > .8) {
				const audioParent = 
					document.getElementById(`playlist-listener-${parentId}`);
				if (audioParent) {
					const existingNextAudio = getAudioElement("next-audio");
					if (!existingNextAudio) {
						const nextAudio = document.createElement("audio");
						nextAudio.addEventListener("timeupdate", timeUpdate);
						nextAudio.classList.add("next-audio");
						nextAudio.preload = "auto";
						//typescript doesn't like me
						//setting style directly
						//and doesn't warn until the build step.
						// @ts-ignore
						nextAudio.style = "display: none";
						queueNext(1);
						audioParent.appendChild(nextAudio);
					}
					else {
						const remainingTime = duration - currentTime;
						if (remainingTime < .2) {
							songEnd();
						}
					}
				}
			}
		}
	};

	useEffect(() => {
		if (!nextUp) return;
		const nextAudio = getAudioElement("next-audio");
		if (nextAudio) {
			nextAudio.src = getDownloadAddress(nextUp.id);
			nextAudio.load();
		}
	},[nextUp]);

	
	return (
		<>
			<Button
				ref={playButtonCtl}
				onClick={() => {
					const currentAudio = getAudioElement("current-audio");
					if (currentAudio) {
						if (!currentAudio.src && !!nextUp) {
							currentAudio.src = getDownloadAddress(nextUp.id);
						}
						if (currentAudio.paused) {
							currentAudio.play();
							if (playButtonCtl.current) {
								playButtonCtl.current.innerText = "Pause";
							}
							if (timeDisplayCtl.current) {
								timeDisplayCtl.current.innerText = "Loading...";
							}
						}
						else {
							currentAudio.pause();
							if (playButtonCtl.current) {
								playButtonCtl.current.innerText = "Play";
							}
						}
					}
				}}
			>
				Play
			</Button>
			<span ref={timeDisplayCtl}>
			</span>
			<div id={`playlist-listener-${parentId}`}>
				<>
					{!!nextUp && <audio
						className="current-audio"
						controls
						preload="auto"
						style={{display: "none"}}
						onTimeUpdate={timeUpdate}
					/>}
				</>
			</div>
		</>
	);
};

