import React, { Component } from 'react';
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import logo from './logo.svg';
import './App.css';

import AddDb from "./components/add-db.component";
import DbDetail from "./components/db.component";
import DbList from "./components/db-list.compoenet";

class App extends Component{
  render() {
    return (
      <Router>
        <div>
          <nav className="navbar navbar-expand navbar-dark bg-dark">
            <a href="/tutorials" className="navbar-brand">
              bezKoder
            </a>
            <div className="navbar-nav mr-auto">
              <li className="nav-item">
                <Link to={"/databases"} className="nav-link">
                  DbList
                </Link>
              </li>
              <li className="nav-item">
                <Link to={"/add_database"} className="nav-link">
                  AddDb
                </Link>
              </li>
            </div>
          </nav>

          <div className="container mt-3">
            <Switch>
              <Route exact path={["/", "/databases"]} component={DbList} />
              <Route exact path="/add_database" component={AddDb} />
              <Route path="/database/:id" component={DbDetail} />
            </Switch>
          </div>
        </div>
      </Router>
    );
  }
}

export default App;
