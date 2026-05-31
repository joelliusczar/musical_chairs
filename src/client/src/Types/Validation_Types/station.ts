import { StationInfo } from "../../Types/station_types";
import { userOptionSchema, actionRuleOptionSchema } from "./user";
import * as Yup from "yup";

export const stationOptionSchema: Yup.ObjectSchema<StationInfo> = Yup.object({
	id: Yup.string().required(),
	name: Yup.string().required(),
	displayname: Yup.string().defined().nullable(),
	isrunning: Yup.boolean().required(),
	owner: userOptionSchema.nullable(),
	rules: Yup.array().of(actionRuleOptionSchema).required(),
	viewsecuritylevel: Yup.number().required(),
	requestsecuritylevel: Yup.number().required(),
	typeid: Yup.number().required(),
});