import {
	NamedIdItem,
	KeyType,
	Named,
	IdType
} from "./generic_types";
import { OwnerParams, User, ActionRule } from "../Types/user_types";
import { PageableListDataShape, SimpleStore } from "./reducer_types"

export interface OwnedStationParams extends OwnerParams {
	stationKey?: KeyType
}

export interface RequiredStationParams extends OwnedStationParams {
	stationKey: KeyType
};

export interface StationInfo extends NamedIdItem {
	displayName: string | null
	isRunning: boolean
	owner: User | null
	rules: ActionRule[]
};

export interface FormStationInfo extends Named {
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

export interface StationTableData<T> extends PageableListDataShape<T> {
	stationRules: ActionRule[]
};

export type StationItemsStore<DataShape> =
	SimpleStore<StationTableData<DataShape>>;