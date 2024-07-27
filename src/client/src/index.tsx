import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import AppRoot from "./AppRoot";


const root = createRoot(document.getElementById("root")!);
root.render(<AppRoot />);

