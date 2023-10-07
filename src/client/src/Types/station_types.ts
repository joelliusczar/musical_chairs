import {
	NamedIdItem,
	KeyType,
	Named,
	IdType,
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
	SimpleStoreShape,
} from "../Reducers/types/reducerTypes";

export interface OwnedStationParams extends OwnerParams {
	stationkey?: KeyType
}

export interface RequiredStationParams extends OwnedStationParams {
	stationkey: KeyType
}

export interface RequiredStationParamsOnly extends OwnerOnlyParam {
	stationkey: KeyType
}

export interface StationInfo extends NamedIdItem {
	displayname: string | null
	isrunning: boolean
	owner: User | null
	rules: ActionRule[]
	viewsecuritylevel: IdType
	requestsecuritylevel: IdType
}

export interface StationInfoForm extends Named {
	id?: IdType
	displayname: string | null
	viewsecuritylevel: NamedIdItem
	requestsecuritylevel: NamedIdItem
}

export interface StationCreationInfo extends Named {
	id?: IdType
	displayname: string | null
	viewsecuritylevel: IdType | number | string
	requestsecuritylevel: IdType | number | string
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

export type StationItemsStore<DataShape> =
	SimpleStoreShape<StationTableData<DataShape>>;