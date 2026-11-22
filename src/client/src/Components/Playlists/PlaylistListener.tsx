import React, {
	useEffect,
	useRef,
	useState,
} from "react";
import { Button } from "@mui/material";
import { SongListDisplayItem } from "../../Types/song_info_types";
import { Calls as SongInfoCalls } from "../../API_Calls/songInfoCalls";
import { Token } from "../../Types/generic_types";
import { GaplessPlayer } from "../../Helpers/audio/gapless_player";

type PlaylistListenerProps = {
	audioItems: SongListDisplayItem[],
	nextUp: SongListDisplayItem | null,
	queueNext: (steps: number) => void,
	parentId: Token,
};

export const PlayStatuses = {
	IDLE: "idle",
	LOADING: "loading",
	PLAYING: "playing",
	PAUSED: "paused",
} as const;

type PlayStatus = typeof PlayStatuses[keyof typeof PlayStatuses];

const ButtonLabels = {
	PLAY: "Play",
	PAUSE: "Pause",
} as const;

const LOADING_MESSAGE = "Loading...";

//stop walking the list if this many tracks in a row fail to load,
//e.g. when the login has expired
const MAX_CONSECUTIVE_FAILURES = 3;

const formatTime = (seconds: number) => {
	const minutes = Math.floor(seconds / 60);
	const wholeSeconds = Math.floor(seconds - (minutes * 60));
	return `${minutes}:${String(wholeSeconds).padStart(2,"0")}`;
};


export const PlaylistListener = (props: PlaylistListenerProps) => {

	const { nextUp, queueNext, parentId } = props;

	const [status, setStatus] = useState<PlayStatus>(PlayStatuses.IDLE);
	const [timeDisplay, setTimeDisplay] = useState("");
	const [nowPlaying, setNowPlaying] =
		useState<SongListDisplayItem | null>(null);

	const playerRef = useRef<GaplessPlayer<SongListDisplayItem> | null>(null);
	//true after asking the parent for the following song, until the new
	//nextUp arrives and is handed to the player
	const awaitingNextRef = useRef(false);
	const hasStartedRef = useRef(false);
	const failuresRef = useRef(0);
	const queueNextRef = useRef(queueNext);
	queueNextRef.current = queueNext;

	const requestNext = () => {
		awaitingNextRef.current = true;
		queueNextRef.current(1);
	};

	const getPlayer = () => {
		if (!playerRef.current) {
			playerRef.current = new GaplessPlayer<SongListDisplayItem>({
				onTrackStart: (item) => {
					hasStartedRef.current = true;
					setNowPlaying(item);
					failuresRef.current = 0;
					setStatus(PlayStatuses.PLAYING);
					//fetch and decode the following song while this one plays,
					//so it is ready to start the instant this one ends
					requestNext();
				},
				onTrackError: (item, error) => {
					console.error(`Could not play ${item.name}`, error);
					failuresRef.current += 1;
					if (failuresRef.current < MAX_CONSECUTIVE_FAILURES) {
						requestNext();
					}
					else {
						playerRef.current?.finish();
					}
				},
				onTimeUpdate: (position, duration) => {
					setTimeDisplay(`${formatTime(position)}/${formatTime(duration)}`);
				},
				onEnded: () => {
					hasStartedRef.current = false;
					setStatus(PlayStatuses.IDLE);
					setTimeDisplay("");
					setNowPlaying(null);
				},
			});
		}
		return playerRef.current;
	};

	useEffect(() => {
		const player = playerRef.current;
		if (!player || !awaitingNextRef.current) return;
		awaitingNextRef.current = false;
		if (nextUp) {
			player.enqueue(
				nextUp,
				SongInfoCalls.songDownload({ id: nextUp.id })
			);
		}
		else {
			player.finish();
		}
	},[nextUp]);

	useEffect(() => {
		return () => {
			playerRef.current?.dispose();
			playerRef.current = null;
			awaitingNextRef.current = false;
			hasStartedRef.current = false;
			failuresRef.current = 0;
			setStatus(PlayStatuses.IDLE);
			setTimeDisplay("");
			setNowPlaying(null);
		};
	},[parentId]);

	const onPlayClick = () => {
		if (status === PlayStatuses.PLAYING || status === PlayStatuses.LOADING) {
			playerRef.current?.pause();
			setStatus(PlayStatuses.PAUSED);
			return;
		}
		if (status === PlayStatuses.PAUSED) {
			playerRef.current?.play();
			setStatus(hasStartedRef.current ?
				PlayStatuses.PLAYING :
				PlayStatuses.LOADING
			);
			return;
		}
		if (!nextUp) return;
		const player = getPlayer();
		//play() must run inside the click handler so the browser
		//allows audio to start
		player.play();
		player.enqueue(
			nextUp,
			SongInfoCalls.songDownload({ id: nextUp.id })
		);
		setStatus(PlayStatuses.LOADING);
		setTimeDisplay(LOADING_MESSAGE);
	};

	const isActive = status === PlayStatuses.PLAYING ||
		status === PlayStatuses.LOADING;

	return (
		<>
			<Button onClick={onPlayClick}>
				{isActive ? ButtonLabels.PAUSE : ButtonLabels.PLAY}
			</Button>
			<span>
				{timeDisplay}
			</span>
			{nowPlaying && <span>
				{" Now playing: "}
				{nowPlaying.name}
				{nowPlaying.artist ? ` - ${nowPlaying.artist}` : ""}
			</span>}
		</>
	);
};
