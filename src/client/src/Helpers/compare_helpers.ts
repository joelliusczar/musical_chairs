import { NamedIdItem } from "../Types/generic_types";
import { User } from "../Types/user_types";

export const userKeyMatch = (key: string, owner: User | null): boolean => {

	if (!owner) {
		return false;
	}
	if (key === owner?.id?.toString()) {
		return true;
	}
	if (key?.toLowerCase() === owner?.username?.toLowerCase()) {
		return true;
	}
	return false;
};

export const keyMatch = (key: string, object: NamedIdItem): boolean => {
	if (key === object?.id?.toString()) {
		return true;
	}
	if (key?.toLowerCase() === object?.name?.toLowerCase()) {
		return true;
	}
	return false;
};