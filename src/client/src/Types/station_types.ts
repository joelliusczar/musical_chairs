import {
	NamedIdItem,
	KeyType,
	Named,
	IdType
} from "./generic_types";
import {
	OwnerParams,
	User,
	ActionRule,
	OwnerOnlyParam,
	SubjectUserParams,
	ActionRuleCreationInfo
} from "../Types/user_types";
import { PageableListDataShape, SimpleStore } from "./reducer_types"

export interface OwnedStationParams extends OwnerParams {
	stationKey?: KeyType
}

export interface RequiredStationParams extends OwnedStationParams {
	stationKey: KeyType
};

export interface RequiredStationParamsOnly extends OwnerOnlyParam {
	stationKey: KeyType
}

export interface StationInfo extends NamedIdItem {
	displayName: string | null
	isRunning: boolean
	owner: User | null
	rules: ActionRule[]
	viewSecurityLevel: IdType
	requestSecurityLevel: IdType
};

export interface StationInfoForm extends Named {
	id?: IdType
	displayName: string | null
	viewSecurityLevel: NamedIdItem
	requestSecurityLevel: NamedIdItem
};

export interface StationCreationInfo extends Named {
	id?: IdType
	displayName: string | null
	viewSecurityLevel: IdType | number | string
	requestSecurityLevel: IdType | number | string
};

export interface StationRuleUpdateParams
	extends RequiredStationParamsOnly, SubjectUserParams {};

export interface StationRuleAddition extends StationRuleUpdateParams {
	rule: ActionRuleCreationInfo
};

export interface StationRuleDeletion extends StationRuleUpdateParams {
	ruleName?: string
};

export interface StationTableData<T> extends PageableListDataShape<T> {
	stationRules: ActionRule[]
};

export type StationItemsStore<DataShape> =
	SimpleStore<StationTableData<DataShape>>;