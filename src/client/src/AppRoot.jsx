import React from "react";
import "./App.css";
import { AppBar, Drawer, ThemeProvider, Typography } from "@material-ui/core";
import { AppRoutes, NavMenu } from "./Components/Navigation/NavRoutes";
import { BrowserRouter } from "react-router-dom";
import { apiAddress } from "./constants";
import { Provider } from "react-redux";
import store from "./reducers";
import { theme, useStyles } from "./style_config";

function AppRoot() {
  const classes = useStyles();

  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        {<BrowserRouter basename="/">
          <div className={classes.root}>
            <AppBar color="primary" position="fixed" className={classes.appBar}>
              <Typography variant="h1">Musical Chairs</Typography>
            </AppBar>
            <Drawer
              variant="permanent"
              anchor="left"
              className={classes.drawer}
              classes={{
                paper: classes.drawerPaper,
              }}
            >
              <NavMenu />
            </Drawer>
            <main className={classes.content}>
              <div className={classes.toolbar} />
              <Typography variant="h1">{apiAddress}</Typography>
              <AppRoutes />
            </main>
          </div>
        </BrowserRouter>}
      </ThemeProvider>
    </Provider>
  );
}

export default AppRoot;
