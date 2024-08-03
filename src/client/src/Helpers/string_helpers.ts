import {
	notNullPredicate,
	squash_sequential_duplicate_chars,
} from "./array_helpers";

export function normalizeOpeningSlash(
	path: string,
	addSlash?: boolean
): string;
export function normalizeOpeningSlash(
	path: null,
	addSlash?: boolean
): null;
export function normalizeOpeningSlash(
	path: string | null,
	addSlash=true
) {
	if (path === null) {
		return null;
	}
	if (addSlash) {
		if (path.length > 0 && path[0] === "/") {
			return path;
		}
		return `/${path}`;
	}
	if (path.length > 0 && path[0] != "/") {
		return path;
	}
	return path.substring(1);
}

export const unicodeToBase64 = (str: string) => {
	const bytes = new TextEncoder().encode(str);
	const binString = Array.from(bytes, (byte) =>
		String.fromCodePoint(byte)
	).join("");
	return btoa(binString);
};

export const base64ToBytes = (base64: string) => {
	const binString = atob(base64)
		.split("")
		.map(m => m.codePointAt(0))
		.filter(notNullPredicate);
	return new Uint8Array(binString);
};

export const base64ToUnicode = (base64: string) => {
	return new TextDecoder().decode(base64ToBytes(base64));
};


export const unicodeToUrlSafeBase64 = (str: string) => {
	return unicodeToBase64(str)
		.replaceAll("+", "-")
		.replaceAll("/", "_");
};

export const urlSafeBase64ToUnicode = (id: string) => {
	const base64 = id
		.replaceAll("-", "+")
		.replaceAll("_", "/");
	return base64ToUnicode(base64);
};


export const prefix_split  = (prefix: string) => {
	const result = prefix
		.split("/")
		.filter(s => !!s)
		.reduce((a, c) => {
			if (a.length) {
				const last = a[a.length - 1];
				a.push(`${last}${c}/`);
				return a;
			}
			else {
				a.push(`${c}/`);
				return a;
			}
		},[] as string[]);
	return result;
};