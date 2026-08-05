import { AlbumInfo } from "../../Types/song_info_types";
import { userOptionSchema, actionRuleOptionSchema } from "./user";
import { artistOptionSchema } from "./artist";
import { stationOptionSchema } from "./station";
import * as Yup from "yup";


export const albumOptionSchema: Yup.ObjectSchema<AlbumInfo> = Yup.object({
	id: Yup.string().required(),
	name: Yup.string().required(),
	owner: userOptionSchema.required(),
	year: Yup.number().defined().nullable(),
	albumartist: artistOptionSchema.defined().nullable(),
	versionnote: Yup.string().optional().nullable(),
	stations: Yup.array().of(stationOptionSchema).optional(),
	rules: Yup.array().of(actionRuleOptionSchema).required(),
});