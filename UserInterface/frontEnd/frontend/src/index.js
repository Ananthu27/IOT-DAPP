import React from "react";
import ReactDOM from "react-dom";
// import App from "./App";

import "./index.css";
import {
  Route,
  NavLink,
  BrowserRouter as Router,
  Switch
} from "react-router-dom";
import Transact from "./Transact";
import Logs from "./Logs";
import Table from "./Table";
import Master from './Master';


const routing = (
  <Router>

    <div className="index" >
    <div className="indo">
      <h2>A DECENTRALIZED BLOCKCHAIN-BASED AUTHENTICATION SYSTEM FOR IOT</h2>
          <NavLink exact activeClassName="active" to="/">
            Home
          </NavLink><br/>
          <NavLink activeClassName="" to="/Transact">
            Transact
          </NavLink><br/>
          <NavLink activeClassName="active" to="/Logs">
            Logs
          </NavLink><br/>
          <NavLink activeClassName="active" to="/Master">
            Master
          </NavLink><br/>
          <NavLink activeClassName="active" to="/Table">
            Group Table
          </NavLink><br/>
     </div>
      <hr />
      <Switch>
        {/* <Route exact path="/" component={App} /> */}
        <Route path="/Transact" component={Transact} />
        <Route path="/Logs" component={Logs} />
        <Route path="/Table"component={Table} />
        <Route path="/Master"component={Master} />

      </Switch>
    </div>
  </Router>
);

ReactDOM.render(routing, document.getElementById("root"));