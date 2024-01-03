

export type RequestBuilder = <SendType, ResponseType>(
	sendParams: SendType
) => {
	abortController: AbortController,
	call: Promise<ResponseType>
};