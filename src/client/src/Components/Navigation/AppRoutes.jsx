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
      <Route
        path="/home"
        render={() => {
          document.title = "Musical Chairs - Home";
          return null;
        }}
      />
      <Route
        path="/queue/:station?"
        render={(props) => {
          document.title = "Musical Chairs - Queue";
          return <Queue {...props} />;
        }}
      />
      <Route
        path="/history/:station?"
        render={(props) => {
          document.title = "Musical Chairs - History";
          return <History {...props}/>;
        }}
      />
    </Switch>
  );
}
