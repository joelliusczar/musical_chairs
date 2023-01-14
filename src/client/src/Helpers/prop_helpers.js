export const conflictWith = (incompatblePropName, propType) => {
	return (props, propName, componentName) => {
		if(props[incompatblePropName] !== undefined && props[propName]) {
			return new Error(`${incompatblePropName} and ${propName}`+
				` cannot both be supplied to ${componentName}`
			);
		}
		if(propType) {
			return propType;
		}
	};
};