import { RequestBuilder } from "../../Types/request_types";

/*
	A decoded (or decoding) track, as a series of PCM segments that play
	back to back with no gap between them.

	The whole-file decoder below yields exactly one segment. A streaming
	decoder (e.g. WebCodecs AudioDecoder) can yield many smaller segments as
	data arrives. The player schedules segments sample-accurately one after
	another, so either kind is gapless as long as each segment is ready
	before the previous one finishes playing.
*/
export interface DecodedTrack {
	segments: AsyncIterable<AudioBuffer>,
}

/*
	Contract for decoders:
	- Start fetching/decoding immediately when called. The player calls the
		decoder as soon as a track is queued (usually while the previous track
		is still playing) and only consumes `segments` later, so lazy work
		would lose the head start that makes the transition gapless.
	- Stop work and reject/finish when `request.abortController` is aborted.
*/
export type TrackDecoder = (
	ctx: BaseAudioContext,
	request: RequestBuilder<ArrayBuffer>
) => DecodedTrack;


const singleSegment = async function* (
	buffer: Promise<AudioBuffer>
): AsyncGenerator<AudioBuffer> {
	yield await buffer;
};

/*
	Downloads the whole file, then decodes it in one go with decodeAudioData.
	Simple and supported everywhere, but playback of the track can't begin
	until the full file has downloaded. With prefetching that only matters
	for the first track (or after a skip).
*/
export const decodeWholeFile: TrackDecoder = (ctx, request) => {
	const buffer = (async () => {
		const bytes = await request.call();
		request.abortController.signal.throwIfAborted();
		return await ctx.decodeAudioData(bytes);
	})();
	//avoid an unhandled rejection warning if the track is cancelled
	//before anyone consumes it; consumers still see the rejection.
	buffer.catch(() => {});
	return { segments: singleSegment(buffer) };
};
