import PropTypes from "prop-types";
import { DontCareMap } from "../Types/generic_types";

export const conflictWith = (
	incompatblePropName: string,
	propType: PropTypes.Requireable<any>
) => {
	return (
		props: DontCareMap,
		propName: string,
		componentName: string,
		location: string,
		propFullName: string
	) => {
		if(props[incompatblePropName] !== undefined && props[propName]) {
			return new Error(`${incompatblePropName} and ${propName}`+
				` cannot both be supplied to ${componentName}`
			);
		}
		if(propType) {
			return propType(props, propName, componentName, location, propFullName);
		}
		return null;
	};
};