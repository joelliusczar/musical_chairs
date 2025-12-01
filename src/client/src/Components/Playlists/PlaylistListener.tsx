import React, { 
	useCallback,
	useEffect,
	useState,
} from "react";
import { Button } from "@mui/material";
import { songDownload } from "../../API_Calls/songInfoCalls";
import { SongListDisplayItem } from "../../Types/song_info_types";

type PlaylistListenerProps = {
	audioItems: SongListDisplayItem[],
	nextUp: SongListDisplayItem | null,
	playNext: (steps: number) => void,
};

export const PlaylistListener = (props: PlaylistListenerProps) => {

	const { nextUp, playNext } = props;
	const [isPlaying, setIsPlaying] = useState(false);
	const [loadedFiles, setLoadedFiles] = useState<ArrayBuffer[]>([]);
	const [audioCtx, setAudioCtx] =  useState<AudioContext | null>(null);
	const [currentTime, setCurrentTime] = useState(0);
	const [totalTime, setTotalTime] = useState(0);
	const [currentDuration, setCurrentDuration] = useState(0);
	const [loadedTitles, setLoadedTitles] = useState<string[]>([""]);

	const formatTime = (seconds: number) => {
		const minutes = Math.floor(seconds / 60);
		const wholeSeconds = Math.floor(seconds - (minutes * 60));
		return `${minutes}:${String(wholeSeconds).padStart(2,"0")}`;
	};

	useEffect(() => {
		const requestObj = songDownload({ id: nextUp?.id || 0 });

		if (nextUp) {
			const fetch = async () => {
				const data = await requestObj.call();

				setLoadedFiles(l => {
					const copy = l.slice(-3);
					copy.push(data);
					return copy;
				});
				setLoadedTitles(l => [...l, nextUp.name]);
			};
			fetch();
		}
		return () => requestObj.abortController.abort();
	},[nextUp, setLoadedFiles, setLoadedTitles]);


	useEffect(() => {
		let hasQueuedNext = false;
		const intervalId = setInterval(() => {
			if (currentDuration)
			{
				const currentTime = (audioCtx?.currentTime || 0) - totalTime;
				const progress = currentTime / currentDuration;
				setCurrentTime(currentTime);
				if (currentDuration < 30 || progress > .8) {
					if (!hasQueuedNext) {
						playNext(1);
						hasQueuedNext = true;
					}
				}
			}
		}, 1000);

		return () => clearInterval(intervalId);
	},[currentDuration, totalTime, playNext, audioCtx, setCurrentTime]);


	const startNext = useCallback(async (audioCtx: AudioContext) => {

		if (!loadedFiles.length) return;

		const loadedFile = loadedFiles[loadedFiles.length - 1];
		const buffer = await audioCtx.decodeAudioData(loadedFile.slice(0));
		const source = audioCtx.createBufferSource();
		source.buffer = buffer;
		source.connect(audioCtx.destination);
		

		setCurrentDuration(buffer.duration);
		setCurrentTime(0);

		source.start();
			

	},[loadedFiles, setCurrentDuration, setCurrentTime]);



	useEffect(() => {
		setCurrentTime(t => {
			setCurrentDuration(duration => {
				if (!audioCtx) return duration;
				const remainingTime = (duration - t);
				setTimeout(() => {
					setTotalTime(a => a + duration);
					setLoadedTitles(l => l.slice(1));
					startNext(audioCtx);
				},remainingTime * 1000);
				return duration;
			});
			return t;
		});
	},[
		startNext, 
		audioCtx, 
		setCurrentDuration, 
		setCurrentTime, 
		setTotalTime,
		setLoadedTitles,
	]);

	useEffect(() => {
		return () => {
			if (audioCtx?.state !== "closed") {
				audioCtx?.close();
			}
		};
	}, [audioCtx]);

	const formattedCurrentTime = formatTime(currentTime);
	const formattedDuration = formatTime(currentDuration || 0);

	return (
		<>
			<Button
				disabled={loadedFiles.length === 0}
				onClick={async () => {
					if (!audioCtx) {
						const ctx = new AudioContext();
						ctx.onstatechange = () => {
							setIsPlaying(ctx.state === "running");
						};
						setAudioCtx(ctx);
						await startNext(ctx);
					}
					else {
						if (audioCtx.state === "running") {
							audioCtx.suspend();
						}
						else {
							audioCtx.resume();
						}
					}
				}}
			>
				{isPlaying ?
					"Pause" :
					"Play"
				}
			</Button>
			<span>
				{`${formattedCurrentTime}/${formattedDuration}`}
			</span>
			<span>{loadedTitles.length > 0 ? loadedTitles[0] : ""}</span>
		</>
	);
};

