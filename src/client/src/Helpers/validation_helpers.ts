import { checkValues } from "../API_Calls/userCalls";
import * as Yup from "yup";

export const validatePhraseIsUnused = async <T>(
	value: string | undefined,
	context: Yup.TestContext<Partial<T>>
) => {
	const used = await checkValues({ values: {
		[context.path]: value,
	}}) as {[key: string]: boolean};
	return !(context.path in used) || !used[context.path];
};