module.exports = {
	"env": {
		"browser": true,
		"node": true,
		"es2021": true,
	},
	"extends": [
		"eslint:recommended",
		"plugin:react/recommended",
	],
	"parserOptions": {
		"ecmaFeatures": {
			"jsx": true,
		},
		"ecmaVersion": 12,
		"sourceType": "module",
	},
	"plugins": [
		"react",
	],
	"rules": {
		"indent": [
			2,
			"tab",
		],
		"no-tabs": 0,
		"linebreak-style": [
			"error",
			"unix",
		],
		"quotes": [
			"error",
			"double",
		],
		"semi": [
			"error",
			"always",
		],
		"comma-dangle": [
			"error",
			{
				"arrays": "always-multiline",
				"objects": "always-multiline",
				"imports": "always-multiline",
			},
		],
		"no-unused-vars": ["warn"],
		"no-console": ["warn", { "allow": ["warn", "error", "info"]}],
		"array-callback-return": "error",
		"max-len": ["error", { "code": 80, "tabWidth": 2 }],
	},
};
