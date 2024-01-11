module.exports = {
	"parser": "@typescript-eslint/parser",
	"env": {
		"browser": true,
		"node": true,
		"es2021": true,
	},
	"extends": [
		"plugin:react/recommended",
		"plugin:@typescript-eslint/recommended",
	],
	"parserOptions": {
		"ecmaFeatures": {
			"jsx": true,
		},
		"ecmaVersion": 12,
		"sourceType": "module",
	},
	"plugins": [
		"@typescript-eslint",
		"react",
		"react-hooks",
		"react-refresh",
	],
	"settings": {
		"react": {
			"version": "detect",
		},
	},
	"root": true,
	"rules": {
		"no-undef": "off",
		"no-unused-vars": "off",

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
		"@typescript-eslint/no-unused-vars": ["warn"],
		"no-console": ["warn", { "allow": ["warn", "error", "info"]}],
		"array-callback-return": "error",
		"max-len": ["error", { "code": 80, "tabWidth": 2 }],
		"react-hooks/rules-of-hooks": "error",
		"react-hooks/exhaustive-deps": "error",
		"react-refresh/only-export-components": "warn",
	},
};
