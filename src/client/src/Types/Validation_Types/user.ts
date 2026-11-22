import { User, ActionRule } from "../../Types/user_types";
import * as Yup from "yup";

export const userOptionSchema: Yup.ObjectSchema<User> = Yup.object({
	id: Yup.number().required(),
	publictoken: Yup.string().required(),
	username: Yup.string().required(),
	displayname: Yup.string().optional(),
});

export const actionRuleOptionSchema: Yup.ObjectSchema<ActionRule> = Yup.object({
	name: Yup.string().required(),
	span: Yup.number().required(),
	quota: Yup.number().required(),
	priority: Yup.number().required(),
	sphere: Yup.string().required(),
	keypath: Yup.string().defined().nullable(),
});