export interface Named {
	name: string
};

export type IdType = number
export type KeyType = string | IdType;

export interface IdItem {
	id: IdType
};


export interface OwnerParam {
	ownerKey: KeyType
}

export interface APIError {
	detail: {
		msg: string
	}[]
}
export interface Error {
	msg: string
}

export interface NamedIdItem extends IdItem, Named {}

export interface SelectItem extends Named {
	id: IdType | number | string
};


export interface Keyed {
	[key: string]: KeyType
};

export interface StringObject {
	[key: string]: string
}

export interface DontCareMap {
	[key: string]: unknown
}

export type SortCallback<T> = (a:T, b:T) => number;
export type SortCallbackFactory = (key: string) => SortCallback<{}>

export type Flags<Type> = {
  [Property in keyof Type]: boolean;
};

export type SingleOrList<OutT, InT extends OutT | OutT[] | null> =
	InT extends OutT[] ? OutT[] :
  InT extends OutT ? OutT : null;