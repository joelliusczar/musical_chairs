import {
	Calls,
} from "../../API_Calls/playlistCalls";
import { PlaylistInfoForm, PlaylistInfo } from "../../Types/playlist_types";
import { stationOptionSchema } from "./station";
import { actionRuleOptionSchema, userOptionSchema } from "./user";
import * as Yup from "yup";

const validatePhraseIsUnused = async (
	value: string | undefined,
	context: Yup.TestContext<Partial<PlaylistInfoForm>>
) => {
	const id = context?.parent?.id;
	if (!value) return true;
	const requestObj = Calls.checkValues({ id, values: {
		[context.path]: value,
	}});
	const used = await requestObj.call();
	return !(context.path in used) || !used[context.path];
};

export const playlistFormSchema: Yup.ObjectSchema<PlaylistInfoForm> = 
Yup.object().shape({
	name: Yup.string().required()
		.matches(/^[a-zA-Z0-9_]*$/, "Name can only contain a-zA-Z0-9_")
		.test(
			"name",
			(value) => `${value.path} is already used`,
			validatePhraseIsUnused
		),
	displayname: Yup.string().optional(),
	viewsecuritylevel: Yup.object().shape({
		id: Yup.number().required(),
		name: Yup.string().required(),
	}).required(),
	stations: Yup.array().of(stationOptionSchema).required(),
});

export const playlistOptionSchema: Yup.ObjectSchema<PlaylistInfo> = Yup.object({
	id: Yup.string().required(),
	name: Yup.string().required(),
	displayname: Yup.string().required(),
	owner: userOptionSchema.required(),
	rules: Yup.array().of(actionRuleOptionSchema).required(),
	viewsecuritylevel: Yup.number().required(),
});