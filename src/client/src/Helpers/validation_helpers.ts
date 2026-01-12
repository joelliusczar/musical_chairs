import { Calls } from "../API_Calls/userCalls";
import * as Yup from "yup";

export const validatePhraseIsUnused = async <T>(
	value: string | undefined,
	context: Yup.TestContext<Partial<T>>
) => {
	const requestObj = Calls.checkValues({ values: {
		[context.path]: value,
	}});
	const used = await requestObj.call() as {[key: string]: boolean};
	return !(context.path in used) || !used[context.path];
};