import compare from "just-compare";

const divmod = (x: number, y: number) => {
	return [Math.floor(x/y), x % y];
};

export const secondsToTuple = (seconds: number)
: [number, number, number, number] => {
	const cleanedSeconds = Math.floor(seconds);
	const [m, s] = divmod(cleanedSeconds, 60);
	const [h, mRemainder] = divmod(m, 60);
	const [d, hRemainder] = divmod(h, 24);
	return [d, hRemainder, mRemainder, s];
};

export const buildTimespanMsg = (
	timeleft: [number, number, number, number]
) => {
	const presentTimeFields = timeleft.map((t,i) => t > 0 ? i : null)
		.filter(i => i !== null);
	const days = timeleft[0] === 1 ? "1 day" : `${timeleft[0]} days`;
	const hours = timeleft[1] ===  1 ? "1 hour" : `${timeleft[1]} hours` ;
	const minutes = timeleft[2] ===  1 ? "1 minute" : `${timeleft[2]} minutes`;
	const seconds = timeleft[3] ===  1 ?  "1 second" : `${timeleft[3]} seconds`;
	if (compare(presentTimeFields, [])) {
		return "";
	}
	if (compare(presentTimeFields, [0])) {
		return days;
	}
	if (compare(presentTimeFields, [1])) {
		return hours;
	}
	if (compare(presentTimeFields, [2])) {
		return minutes;
	}
	if (compare(presentTimeFields, [3])) {
		return seconds;
	}
	if (compare(presentTimeFields, [0,1])) {
		return `${days} and ${hours}`;
	}
	if (compare(presentTimeFields, [0,2])) {
		return `${days} and ${minutes}`;
	}
	if (compare(presentTimeFields, [0,3])) {
		return `${days} and ${seconds}`;
	}
	if (compare(presentTimeFields, [1,2])) {
		return `${hours} and ${minutes}`;
	}
	if (compare(presentTimeFields, [1,3])) {
		return `${hours} and ${seconds}`;
	}
	if (compare(presentTimeFields, [2,3])) {
		return `${minutes} and ${seconds}`;
	}
	if (compare(presentTimeFields, [0,1,2])) {
		return `${days}, ${hours} and ${minutes}`;
	}
	if (compare(presentTimeFields, [0,1,3])) {
		return `${days}, ${hours} and ${seconds}`;
	}
	if (compare(presentTimeFields, [0,2,3])) {
		return `${days}, ${minutes} and ${seconds}`;
	}
	if (compare(presentTimeFields, [1,2,3])) {
		return `${hours}, ${minutes} and ${seconds}`;
	}
	return `${days}, ${hours}, ${minutes} and ${seconds}`;
};