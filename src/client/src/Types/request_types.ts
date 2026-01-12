

export type RequestBuilder<ResponseType> = {
	abortController: AbortController,
	call: () => Promise<ResponseType>
};