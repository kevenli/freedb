import React, {Component} from "react";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import {Link} from "react-router-dom";
import FreedbDataService from "../services/freedb.service";
import { LinkContainer } from 'react-router-bootstrap'
import { Card } from 'react-bootstrap';

export default class CollectionView extends Component {
  constructor(props){
    super(props);
    this.queryCollection = this.queryCollection.bind(this);

    this.state = {
      db_name: "",
      col_name: "",
      docs: [],
      total_rows: 0,
      skip: 0,
      paging:{}
    }
  }

  componentDidMount() {
    this.setState({
      db_name: this.props.match.params.db_name,
      col_name: this.props.match.params.col_name
    }, ()=>{
      this.queryCollection();
    });
  }

  queryCollection(){
    FreedbDataService.queryCollection(this.state.db_name, this.state.col_name)
        .then(response=>{
          this.setState({
            docs: response.data.data,
            paging: response.data.paging
          })
        }).catch(e=>{
      console.log(e);
    });
  }

  render() {
    const {docs} = this.state;
    return <div>
      <Breadcrumb>
        <LinkContainer to={`/databases/${this.state.db_name}`} >
        <Breadcrumb.Item>
            {this.state.db_name}
        </Breadcrumb.Item>
        </LinkContainer>
        <Breadcrumb.Item>
          {this.state.col_name}
        </Breadcrumb.Item>
      </Breadcrumb>
      {docs &&
      docs.map((doc, index) => (
          <Card>
            <Card.Body>
            <pre>
              {JSON.stringify(doc, undefined, 2)}</pre>
            </Card.Body>
          </Card>
      ))}
    </div>

  }
}
