import { KeyValue, IdItem } from "../Types/generic_types";
import { PageableParams } from "./pageable_types";

export interface OwnerOnlyParam {
	ownerkey: string | number
}

export type OwnerParams = PageableParams & OwnerOnlyParam

export interface SubjectUserParams {
	subjectuserkey: string | number
};

export interface ActionRuleCreationInfo {
	name: string
	span: number
	quota: number
};

export interface ActionRule extends ActionRuleCreationInfo {
	priority: number
	sphere: string
	keypath: string | null
};


export interface RoledEntity {
	roles: ActionRule[]
};


export interface User extends IdItem {
	publictoken: string
	username: string
	displayname?: string
}

export interface RoledUser extends User, RoledEntity {};


export interface EmailableUser extends RoledUser {
	email: string
}


export interface UserBasicUpdate {
	email: string
	displayname?: string
};

export interface UserBasicUpdateApiParams extends SubjectUserKeyItem {
	data: UserBasicUpdate
}

export interface LoggedInUser extends RoledEntity, IdItem {
	username: string,
	access_token: string,
	lifetime: number,
	login_timestamp: number,
};

export interface LoginCredentials {
	username: string,
	password: string,
};

export interface PasswordUpdate {
	oldpassword: string,
	newpassword: string,
};

export interface SubjectPasswordUpdate
	extends PasswordUpdate, SubjectUserParams {}


export interface UserCreationInfo extends User, RoledEntity{
	email: string
	displayname?: string
	password: string
	passwordconfirm: string
};

export interface SubjectUserKeyItem {
	subjectuserkey: KeyValue
};

export interface SubjectUserRoleAddition extends SubjectUserKeyItem {
	rule: ActionRuleCreationInfo
};

export interface SubjectUserRoleDeletion extends SubjectUserKeyItem {
	rulename?: string
};

export interface ExistenceCheckParams {
	username?: string
	email?: string
};