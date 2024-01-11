export interface Named {
	name: string
};

export type IdValue = number
export type KeyValue = string | IdValue;

export interface IdItem {
	id: IdValue
};


export interface OwnerParam {
	ownerkey: KeyValue
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
	id: IdValue | number | string
};


export interface Keyed {
	[key: string]: KeyValue
};

export interface StringObject {
	[key: string]: string
}

export interface DontCareMap {
	[key: string]: unknown
}

export interface Dictionary<T> {
	[key: KeyValue]: T
}

export type SortCallback<T> = (a:T, b:T) => number;
export type SortCallbackFactory = 
<T, K extends keyof T>(key: K) => SortCallback<T>

export type Flags<Type> = {
  [Property in keyof Type]: boolean;
};

export type SingleOrList<OutT, InT extends OutT | OutT[] | null> =
	InT extends OutT[] ? OutT[] :
  InT extends OutT ? OutT : null;



type PropsCoercedToPorNeverOnO<P, O> = {
	[ k in keyof O]: O[k] extends P ? k : never 
}[keyof O];	

export type PropsOfTypePOnO<P, O>= {
	[k in PropsCoercedToPorNeverOnO<P, O> ]: P
}