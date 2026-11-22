import { defaultWebClient } from "../../API_Calls/api";

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
	- Stop work and reject/finish when `signal` is aborted.
*/
export type TrackDecoder = (
	ctx: BaseAudioContext,
	url: string,
	signal: AbortSignal
) => DecodedTrack;


const getAuthHeaders = (): HeadersInit => {
	const auth = defaultWebClient.defaults.headers.common["Authorization"];
	return typeof auth === "string" && auth ? { Authorization: auth } : {};
};

export const fetchAudioResponse = async (
	url: string,
	signal: AbortSignal
): Promise<Response> => {
	//the download endpoint accepts either the bearer header or the
	//access_token cookie, so send both like the rest of the app does
	const response = await fetch(url, {
		credentials: "include",
		headers: getAuthHeaders(),
		signal,
	});
	if (!response.ok) {
		throw new Error(`Failed to download ${url}: ${response.status}`);
	}
	return response;
};

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
export const decodeWholeFile: TrackDecoder = (ctx, url, signal) => {
	const buffer = (async () => {
		const response = await fetchAudioResponse(url, signal);
		const bytes = await response.arrayBuffer();
		signal.throwIfAborted();
		return await ctx.decodeAudioData(bytes);
	})();
	//avoid an unhandled rejection warning if the track is cancelled
	//before anyone consumes it; consumers still see the rejection.
	buffer.catch(() => {});
	return { segments: singleSegment(buffer) };
};
