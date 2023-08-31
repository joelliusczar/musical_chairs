import { createTheme } from "@mui/material/styles";

export const h1Size = 34;
export const fontDecSize = 2;
export const drawerWidth = 240;

const calcHeaderFontSize = (headerNum: number) => {
	return h1Size - (headerNum - 1) * fontDecSize;
};

export const theme = createTheme({
	typography: {
		h1: {
			fontSize: calcHeaderFontSize(1),
		},
		h2: {
			fontSize: calcHeaderFontSize(2),
		},
		h3: {
			fontSize: calcHeaderFontSize(3),
		},
		h4: {
			fontSize: calcHeaderFontSize(4),
		},
		h5: {
			fontSize: calcHeaderFontSize(5),
		},
		h6: {
			fontSize: calcHeaderFontSize(6),
		},
	},
});