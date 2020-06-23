import React, {Component, Fragment} from "react";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import {Link} from "react-router-dom";
import FreedbDataService from "../services/freedb.service";
import { LinkContainer } from 'react-router-bootstrap'
import { Card, Button, ButtonGroup, FormText, Form, InputGroup, FormControl } from 'react-bootstrap';

export default class CollectionView extends Component {
  constructor(props){
    super(props);
    this.queryCollection = this.queryCollection.bind(this);
    this.btnNewDocClick = this.btnNewDocClick.bind(this);
    this.btnCancelNewDoc = this.btnCancelNewDoc.bind(this);
    this.updateNewDoc = this.updateNewDoc.bind(this);
    this.btnSaveNewDoc = this.btnSaveNewDoc.bind(this);
    this.textQueryChange = this.textQueryChange.bind(this);
    this.btnQueryClick = this.btnQueryClick.bind(this);
    this.txtSkipChange = this.txtSkipChange.bind(this);

    this.state = {
      db_name: "",
      col_name: "",
      docs: [],
      total_rows: 0,
      skip: 0,
      paging:{},
      showNewDocView: false,
      newDocStr: "",
      queryStr: ""
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

  btnNewDocClick(e){
    this.setState({
      showNewDocView: true
    })
  }

  btnCancelNewDoc(e){
    this.setState({
      showNewDocView: false
    })
  }

  updateNewDoc(e){
    this.setState({
      newDocStr: e.target.value
    })
  }

  btnSaveNewDoc(e){
    FreedbDataService.saveDoc(this.state.db_name, this.state.col_name, this.state.newDocStr)
        .then(response=>{
          this.setState({
            showNewDocView: false
          })
        })
        .catch(error=>{
          console.log(error)
        })
  }

  textQueryChange(e){
    this.setState({
      queryStr: e.target.value
    })
  }

  txtSkipChange(e){
    this.setState({
      skip: parseInt(e.target.value)
    })
  }

  btnQueryClick(){
    this.queryCollection();
  }

  queryCollection(){
    let query={};
    try{
      query = JSON.parse(this.state.queryStr);
    }
    catch(SyntaxError){
      query = {}
    }
    FreedbDataService.queryCollection(this.state.db_name, this.state.col_name, query, this.state.skip)
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
        <ButtonGroup className="ml-auto px-2" >
          <Button variant="outline-dark" onClick={this.btnNewDocClick}>New Doc</Button>
          <Button variant="outline-dark">Delete Collection</Button>
        </ButtonGroup>
      </Breadcrumb>
      {this.state.showNewDocView &&
          <Form>
            <Form.Group>
            <Form.Control as="textarea" rows="3" value={this.state.newDocStr} onChange={this.updateNewDoc}/>
            </Form.Group>
            <Button onClick={this.btnSaveNewDoc}>Save</Button>
            <Button onClick={this.btnCancelNewDoc}>Cancel</Button>
          </Form>
      }
      <Fragment>
        <Form>
          <Form.Row>
            <InputGroup className="my-inline-group">
              <InputGroup.Prepend>
                <InputGroup.Text>Query</InputGroup.Text>
              </InputGroup.Prepend>
              <FormControl id="query" defaultValue="{}" onChange={this.textQueryChange} />
              <InputGroup.Append>
                <Button onClick={this.btnQueryClick}>Go</Button>
              </InputGroup.Append>

            </InputGroup>
            <InputGroup className="my-inline-group">
              <InputGroup.Prepend>
                <InputGroup.Text>Skip</InputGroup.Text>
              </InputGroup.Prepend>
              <FormControl id="skip" defaultValue="0" onChange={this.txtSkipChange} />
            </InputGroup>
          </Form.Row>
        </Form>
      </Fragment>

      {docs &&
      docs.map((doc, index) => (
          <Card key={doc.id}>
            <Card.Body>
            <pre>
              {JSON.stringify(doc, undefined, 2)}</pre>
            </Card.Body>
          </Card>
      ))}
    </div>

  }
}
