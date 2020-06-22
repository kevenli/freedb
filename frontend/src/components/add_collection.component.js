import React, {Component} from 'react';
import FreedbDataService from "../services/freedb.service";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import {Redirect} from "react-router-dom";

export default class AddCollection extends Component{
  constructor(props){
    super(props);
    this.onChangeCollectionName = this.onChangeCollectionName.bind(this);
    this.saveCollection = this.saveCollection.bind(this);


    this.state = {
      db_name: "",
      new_collection_name:"",
      redirectDbDetail: false
    };
  }

  componentDidMount() {
    this.setState({db_name: this.props.match.params.db_name})
  }

  onChangeCollectionName(e){
    this.setState({
      new_collection_name: e.target.value
    });
  }

  saveCollection(e){
    FreedbDataService.createCollection(this.state.db_name,
      {name: this.state.new_collection_name})
      .then(response=>{
        this.setState({redirectDbDetail:true});
      })
      .catch(e=>{

      });
    e.preventDefault();
  }

  render(){
    if (this.state.redirectDbDetail){
      return <Redirect to={`/databases/${this.state.db_name}`}/>
    }
    return <div>
      <h1>{this.state.db_name}</h1>
      <Form>
        <Form.Group controlId="formCollectionName">
          <Form.Label>Collection Name</Form.Label>
          <Form.Control type="text" placeholder="Enter collection name"
            onChange={this.onChangeCollectionName}/>
          <Form.Text className="text-muted" name="name" >
          </Form.Text>
        </Form.Group>
        <button onClick={this.saveCollection} className="btn btn-success">
              Submit
            </button>
      </Form>
    </div>
  }
}