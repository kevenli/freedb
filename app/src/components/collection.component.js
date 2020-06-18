import React, {Component} from "react";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import {Link} from "react-router-dom";
import FreedbDataService from "../services/freedb.service";

export default class CollectionView extends Component {
  constructor(props){
    super(props);
    this.queryCollection = this.queryCollection.bind(this);

    this.state = {
      db_name: "",
      col_name: "",
      docs: []
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
            docs: response.data
          })
        }).catch(e=>{
      console.log(e);
    });
  }

  render() {
    const {docs} = this.state;
    return <div>
        <Breadcrumb.Item as={Link} to={`/databases/${this.state.db_name}`}>
            {this.state.db_name}
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          {this.state.col_name}
        </Breadcrumb.Item>
      {docs &&
      docs.map((doc, index) => (
          <div>
            <pre>
              {JSON.stringify(doc, undefined, 2)}</pre></div>
      ))}
    </div>

  }
}
