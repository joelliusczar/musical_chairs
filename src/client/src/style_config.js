import { unstable_createMuiStrictModeTheme as createMuiTheme, 
	makeStyles} from "@mui/material";

const h1Size = 34;
const fontDecSize = 2;
const drawerWidth = 240;

const calcHeaderFontSize = (headerNum) => {
	return h1Size - (headerNum - 1) * fontDecSize;
};

export const theme = createMuiTheme({
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

export const useStyles = makeStyles((theme) => ({
	root: {
		display: "flex",
	},
	appBar: {
		marginLeft: drawerWidth,
		width: `calc(100% - ${drawerWidth}px)`,
	},
	content: {
		flexGrow: 1,
		padding: theme.spacing(3),
	},
	drawer: {
		flexShrink: 0,
		width: drawerWidth,
	},
	drawerPaper: {
		width: drawerWidth,
	},
	toolbar: theme.mixins.toolbar,
}));