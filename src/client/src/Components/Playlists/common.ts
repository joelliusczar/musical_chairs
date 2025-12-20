import {
	Calls,
} from "../../API_Calls/playlistCalls";
import * as Yup from "yup";
import {
	PlaylistInfoForm,
} from "../../Types/playlist_types";
import { 
	RulePriorityLevel,
} from "../../constants";


export const validatePhraseIsUnused = async (
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

export const viewSecurityOptions = [
	{
		id: RulePriorityLevel.PUBLIC,
		name: "Public",
	},
	{
		id: RulePriorityLevel.ANY_USER,
		name: "Any User",
	},
	{
		id: RulePriorityLevel.INVITED_USER,
		name: "Invited Users Only",
	},
	{
		id: RulePriorityLevel.OWENER_USER,
		name: "Private",
	},
];