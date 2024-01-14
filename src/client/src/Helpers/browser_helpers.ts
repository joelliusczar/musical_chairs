import { StringObject } from "../Types/generic_types";

export const cookieToObject = (cookie: string): StringObject => {
	const kvps = cookie.split(";");
	const obj: StringObject = {};
	for(const pair of kvps) {
		if (!pair) continue;
		const pairSplit = pair.split("=");
		obj[pairSplit[0].trim()] = pairSplit[1].trim();
	}
	return obj;
};

export const cookieToObjectURIDecoded = (cookie: string): StringObject => {
	const cookieObj = cookieToObject(cookie);
	const result: StringObject = {};
	Object.keys(cookieObj).forEach(key => {
		result[key] = decodeURIComponent(cookieObj[key] || "");
	});
	return result;
};

export const getUsernameCookie = (cookie: string) => {
	const cookieObj = cookieToObject(cookie);
	const usernameCookie = decodeURIComponent(cookieObj["username"] || "");
	return usernameCookie;
};