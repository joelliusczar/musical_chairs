import React from "react";
import { Route, Switch, NavLink } from "react-router-dom";
import { List, ListItem } from "@material-ui/core";
import Queue from "../Queue/Queue";
import History from "../History/History";

export function NavMenu() {
  return (
    <List>
      <ListItem button>
        <NavLink to="/home">Home</NavLink>
      </ListItem>
      <ListItem button>
        <NavLink to="/queue/">Queue</NavLink>
      </ListItem>
      <ListItem button>
        <NavLink to="/history">History</NavLink>
      </ListItem>
    </List>
  );
}

export function AppRoutes() {
  return (
    <Switch>
      <Route path="/queue/:station?">
        <Queue />
      </Route>
      <Route path="/history/:station?">
        <History />
      </Route>
    </Switch>
  );
}
