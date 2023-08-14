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
};