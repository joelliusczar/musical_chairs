import {
	NamedIdItem,
	KeyValue,
	Named,
	IdValue,
} from "./generic_types";
import {
	OwnerParams,
	User,
	ActionRule,
	OwnerOnlyParam,
	SubjectUserParams,
	ActionRuleCreationInfo,
} from "../Types/user_types";
import {
	PageableListDataShape,
} from "./reducerTypes";

export interface OwnedStationParams extends OwnerParams {
	stationkey?: KeyValue
}

export interface RequiredStationParams extends OwnedStationParams {
	stationkey: KeyValue
}

export interface RequiredStationParamsOnly extends OwnerOnlyParam {
	stationkey: KeyValue
}

export interface StationInfo extends NamedIdItem {
	displayname: string | null
	isrunning: boolean
	owner: User | null
	rules: ActionRule[]
	viewsecuritylevel: IdValue
	requestsecuritylevel: IdValue
}

export interface StationInfoForm extends Named {
	id?: IdValue
	displayname: string | null
	viewsecuritylevel: NamedIdItem
	requestsecuritylevel: NamedIdItem
}

export interface StationCreationInfo extends Named {
	id?: IdValue
	displayname: string | null
	viewsecuritylevel: IdValue | number | string
	requestsecuritylevel: IdValue | number | string
};

export interface StationRuleUpdateParams
	extends RequiredStationParamsOnly, SubjectUserParams {};

export interface StationRuleAddition extends StationRuleUpdateParams {
	rule: ActionRuleCreationInfo
};

export interface StationRuleDeletion extends StationRuleUpdateParams {
	rulename?: string
};

export interface StationTableData<T> extends PageableListDataShape<T> {
	stationrules: ActionRule[]
};