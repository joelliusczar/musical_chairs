import { KeyType, IdItem } from "../Types/generic_types";
import { PageableParams } from "./pageable_types";

export interface OwnerOnlyParam {
	ownerKey: string | number
}

export interface OwnerParams extends PageableParams, OwnerOnlyParam {}

export interface SubjectUserParams {
	subjectUserKey: string | number
};

export interface ActionRuleCreationInfo {
	name: string
	span: number
	count: number
};

export interface ActionRule extends ActionRuleCreationInfo {
	priority: number
	domain: string
};

export interface PathsActionRule extends ActionRule {
	path: string | null
};

export interface RoledEntity {
	roles: ActionRule[]
};

export interface RoledUser extends IdItem, RoledEntity {};

export interface UserBase extends IdItem {
	username: string
	email: string
	displayName?: string
}

export interface User extends UserBase, RoledUser {};

export interface UserBasicUpdate {
	email: string
	displayName?: string
};

export interface UserBasicUpdateApiParams extends SubjectUserKeyItem {
	data: UserBasicUpdate
}

export interface LoggedInUser extends RoledEntity {
	username: string,
	access_token: string,
	lifetime: number,
};

export interface LoginCredentials {
	username: string,
	password: string,
};

export interface PasswordUpdate {
	oldPassword: string,
	newPassword: string,
};

export interface SubjectPasswordUpdate
	extends PasswordUpdate, SubjectUserParams {}


export interface UserCreationInfo extends User, RoledEntity{
	email: string
	displayName?: string
	password: string
	passwordConfirm: string
};

export interface SubjectUserKeyItem {
	subjectUserKey: KeyType
};

export interface SubjectUserRoleAddition extends SubjectUserKeyItem {
	rule: ActionRuleCreationInfo
};

export interface SubjectUserRoleDeletion extends SubjectUserKeyItem {
	ruleName?: string
};

export interface ExistenceCheckParams {
	username?: string
	email?: string
};