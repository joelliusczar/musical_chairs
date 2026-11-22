import {
	DecodedTrack,
	TrackDecoder,
	decodeWholeFile,
} from "./track_decoders";
import { RequestBuilder } from "../../Types/request_types";

//headroom when something has to start "now": scheduling exactly at
//currentTime can clip the first few milliseconds.
const START_LEAD_SECONDS = 0.1;
const TICK_MS = 250;

/*
	Something the player can put on its timeline.

	The player only needs to know when a track starts, when it ends and how
	to stop it, all on the AudioContext clock. `schedule` starts the track at
	`startAt` (or as soon as possible if that time has passed) and resolves
	with the time the track will end. The player starts the next track at
	exactly that time.

	BufferedTrack (below) plays decoded PCM and knows its end time exactly.
	A hybrid first track could implement this same interface by playing an
	<audio> element through a MediaElementAudioSourceNode on the player's
	context, and resolving `schedule` shortly before the element finishes
	with an end time estimated from the element's duration and currentTime.
	The player wouldn't need to change.
*/
export interface PlayableTrack {
	readonly startTime: number | null,
	readonly endTime: number | null,
	//seconds of audio known so far; final once endTime is set
	readonly duration: number,
	schedule(
		ctx: AudioContext,
		destination: AudioNode,
		startAt: number
	): Promise<number>,
	stop(): void,
}


export class BufferedTrack implements PlayableTrack {
	startTime: number | null = null;
	endTime: number | null = null;
	duration = 0;
	private nodes: AudioBufferSourceNode[] = [];
	private stopped = false;

	constructor(
		private decoded: DecodedTrack,
		private controller: AbortController
	) {}

	async schedule(
		ctx: AudioContext,
		destination: AudioNode,
		startAt: number
	): Promise<number> {
		let cursor = startAt;
		for await (const segment of this.decoded.segments) {
			if (this.stopped) break;
			const earliest = ctx.currentTime + START_LEAD_SECONDS;
			if (cursor < earliest) {
				//data arrived after it should already have been playing.
				//A gap is unavoidable here; start as soon as possible.
				cursor = earliest;
			}
			const node = ctx.createBufferSource();
			node.buffer = segment;
			node.connect(destination);
			node.onended = () => {
				node.disconnect();
				this.nodes = this.nodes.filter(n => n !== node);
			};
			node.start(cursor);
			this.nodes.push(node);
			if (this.startTime === null) {
				this.startTime = cursor;
			}
			cursor += segment.duration;
			this.duration += segment.duration;
		}
		this.endTime = cursor;
		return cursor;
	}

	stop() {
		this.stopped = true;
		this.controller.abort();
		for (const node of this.nodes) {
			node.onended = null;
			try {
				node.stop();
			}
			catch {
				//never started; nothing to stop
			}
			node.disconnect();
		}
		this.nodes = [];
	}
}


export interface GaplessPlayerEvents<T> {
	//the track has become audible
	onTrackStart?: (info: T) => void,
	//the track could not be loaded or decoded and was dropped
	onTrackError?: (info: T, error: unknown) => void,
	onTimeUpdate?: (position: number, duration: number) => void,
	//finish() was called and everything queued has played
	onEnded?: () => void,
}

type TimelineEntry<T> = {
	info: T,
	track: PlayableTrack,
	started: boolean,
	removed: boolean,
};


export class GaplessPlayer<T> {
	private ctx: AudioContext | null = null;
	private output: GainNode | null = null;
	private entries: TimelineEntry<T>[] = [];
	private nextStartTime = 0;
	//tracks are scheduled strictly in order, each one at the end of the last
	private scheduling: Promise<void> = Promise.resolve();
	private tickHandle: ReturnType<typeof setInterval> | null = null;
	private noMoreTracks = false;
	private endedNotified = false;
	private disposed = false;

	constructor(
		private events: GaplessPlayerEvents<T>,
		private decoder: TrackDecoder = decodeWholeFile
	) {}

	private getContext(): { ctx: AudioContext, output: GainNode } {
		if (!this.ctx || !this.output) {
			this.ctx = new AudioContext();
			this.output = this.ctx.createGain();
			this.output.connect(this.ctx.destination);
		}
		return { ctx: this.ctx, output: this.output };
	}

	/*
		The first call must happen inside a user gesture (e.g. a click
		handler); browsers keep an AudioContext silent until then.
	*/
	play(): Promise<void> {
		const { ctx } = this.getContext();
		this.startTicking();
		return ctx.resume();
	}

	pause(): Promise<void> {
		this.stopTicking();
		return this.ctx ? this.ctx.suspend() : Promise.resolve();
	}

	/*
		Queue a track to play after everything already queued.
		Downloading and decoding start right away.
	*/
	enqueue(info: T, request: RequestBuilder<ArrayBuffer>) {
		if (this.disposed) return;
		const { ctx, output } = this.getContext();
		const track = new BufferedTrack(
			this.decoder(ctx, request),
			request.abortController
		);
		this.addTrack(info, track, ctx, output);
	}

	addTrack(
		info: T,
		track: PlayableTrack,
		ctx: AudioContext,
		output: AudioNode
	) {
		const entry: TimelineEntry<T> = {
			info,
			track,
			started: false,
			removed: false,
		};
		this.entries.push(entry);
		this.noMoreTracks = false;
		this.endedNotified = false;
		this.scheduling = this.scheduling.then(async () => {
			if (this.disposed || entry.removed) return;
			try {
				this.nextStartTime = await track.schedule(
					ctx,
					output,
					this.nextStartTime
				);
			}
			catch (error) {
				if (this.disposed || entry.removed) return;
				this.removeEntry(entry);
				this.events.onTrackError?.(info, error);
			}
		});
	}

	//nothing more will be queued; fire onEnded once the queue drains
	finish() {
		this.noMoreTracks = true;
		this.tick();
	}

	dispose() {
		this.disposed = true;
		this.stopTicking();
		for (const entry of this.entries) {
			entry.removed = true;
			entry.track.stop();
		}
		this.entries = [];
		this.ctx?.close().catch(() => {});
		this.ctx = null;
		this.output = null;
	}

	private removeEntry(entry: TimelineEntry<T>) {
		entry.removed = true;
		entry.track.stop();
		this.entries = this.entries.filter(e => e !== entry);
	}

	private startTicking() {
		if (this.tickHandle !== null) return;
		this.tickHandle = setInterval(() => this.tick(), TICK_MS);
	}

	private stopTicking() {
		if (this.tickHandle === null) return;
		clearInterval(this.tickHandle);
		this.tickHandle = null;
	}

	private tick() {
		if (this.disposed) return;
		const now = this.ctx?.currentTime ?? 0;

		//release tracks that have finished playing so their audio can be
		//garbage collected
		while (this.entries.length) {
			const endTime = this.entries[0].track.endTime;
			if (endTime === null || endTime > now) break;
			const finished = this.entries.shift();
			finished?.track.stop();
		}

		const current = this.entries[0];
		const startTime = current?.track.startTime;
		if (current && startTime !== null && startTime <= now) {
			if (!current.started) {
				current.started = true;
				this.events.onTrackStart?.(current.info);
			}
			const duration = current.track.duration;
			const position = Math.min(Math.max(now - startTime, 0), duration);
			this.events.onTimeUpdate?.(position, duration);
		}

		if (!this.entries.length && this.noMoreTracks && !this.endedNotified) {
			this.endedNotified = true;
			this.stopTicking();
			this.events.onEnded?.();
		}
	}
}
