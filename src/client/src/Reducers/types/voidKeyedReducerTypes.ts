import { KeyType } from "../../Types/generic_types";
import {
	WaitingTypes,
	KeyAndData,
	KeyedStoreShape,
	VoidStoreShape
} from "./reducerTypes";


export type VoidKeyedActionPayload = {
	type: WaitingTypes.started,
	payload: { key: KeyType }
} |  {
	type: WaitingTypes.restart,
	payload: { key: KeyType }
} |  {
	type: WaitingTypes.done,
	payload: { key: KeyType }
} | {
	type: WaitingTypes.failed,
	payload: KeyAndData<string>
} | {
	type: WaitingTypes.reset,
	payload: { key: KeyType }
};

type StatusChange = WaitingTypes.started |
	WaitingTypes.restart |
	WaitingTypes.done |
	WaitingTypes.reset;

export type VoidKeyedUnionSelect =
	{
	[key in StatusChange]: (
		state: KeyedStoreShape<VoidStoreShape>,
		payload: { key: KeyType }
	) => KeyedStoreShape<VoidStoreShape>
	} &
	{
		[key in WaitingTypes.failed]: (
			state: KeyedStoreShape<VoidStoreShape>,
			payload: KeyAndData<string>
		) => KeyedStoreShape<VoidStoreShape>
	};
