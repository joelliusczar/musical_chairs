import { KeyType, IdItem } from "../Types/generic_types";
import { PageableParams } from "./pageable_types";

export interface OwnerParams extends PageableParams {
	ownerKey: string | number
}

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

export interface User extends RoledUser {
	username: string
	displayName: string | null
};

export interface LoggedInUser extends RoledEntity {
	username: string,
	access_token: string,
	lifetime: number,
};

export interface LoginCredentials {
	username: string,
	password: string,
};
export interface UserBase extends User {
	email: string
	displayName: string | null
};

export interface UserCreationInfo extends UserBase, RoledEntity{
	password: string
};

export interface SubjectUserKeyItem {
	subjectUserKey: KeyType
};

export interface ExistenceCheckParams {
	username?: string
	email?: string
};