
export class VoidStore {
	callStatus: string | null = null
	error: string | null = null
}


export class RequiredDataStore<T> extends VoidStore {
	data: T

	constructor(data: T) {
		super();
		this.data = data;
	}
}