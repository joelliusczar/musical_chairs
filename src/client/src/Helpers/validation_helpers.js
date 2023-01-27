import { checkValues } from "../API_Calls/userCalls";

export const validatePhraseIsUnused = async (value, context) => {
	const used = await checkValues({ values: {
		[context.path]: value,
	}});
	return !(context.path in used) || !used[context.path];
};