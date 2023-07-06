export const cookieToObject = (cookie) => {
	const kvps = cookie.split(";");
	const obj = {};
	for(const pair of kvps) {
		if (!pair) continue;
		const pairSplit = pair.split("=");
		obj[pairSplit[0].trim()] = pairSplit[1].trim();
	}
	return obj;
};