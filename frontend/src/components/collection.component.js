import React, {Component, Fragment} from "react";
import Breadcrumb from "react-bootstrap/Breadcrumb";
import FreedbDataService from "../services/freedb.service";
import { LinkContainer } from 'react-router-bootstrap'
import {Card, Button, ButtonGroup, FormText, Form, InputGroup, FormControl, Modal} from 'react-bootstrap';
import { Link } from 'react-router-dom';

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
    this.txtSortChange = this.txtSortChange.bind(this);
    this.txtLimitChange = this.txtLimitChange.bind(this);
    this.btnImportDataClick = this.btnImportDataClick.bind(this);
    this.btnUploadFileClick = this.btnUploadFileClick.bind(this);

    this.state = {
      db_name: "",
      col_name: "",
      docs: [],
      total_rows: 0,
      rows_count: 0,
      skip: 0,
      paging:{},
      showNewDocView: false,
      newDocStr: "",
      queryStr: "{}",
      sortStr:"",
      limit:20,
      showImportDataDialog: false,
      uploadFile: null
    }
  }

  componentDidMount() {
    const params = new URLSearchParams(this.props.location.search)
    let skip=parseInt(params.get('skip'));
    if (isNaN(skip)){
      skip = 0;
    }

    this.setState({
      db_name: this.props.match.params.db_name,
      col_name: this.props.match.params.col_name,
      skip: skip
    }, ()=>{
      this.queryCollection();
    });
  }

  componentWillReceiveProps(nextProps){
    if (nextProps.id === this.props.id){
      const params = new URLSearchParams(nextProps.location.search)
      let skip=parseInt(params.get('skip'));
      if (isNaN(skip)){
        skip = 0;
      }

      this.setState({
        skip: skip
      }, ()=>{
        this.queryCollection();
      });
    }
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

  btnImportDataClick(){
    this.setState({
      showImportDataDialog: true
    })
  }

  textQueryChange(e){
    this.setState({
      queryStr: e.target.value
    })
  }

  txtSkipChange(e){
    let inputSkip = parseInt(e.target.value);
    if (isNaN(inputSkip)){
      inputSkip = 0;
    }
    this.setState({
      skip: inputSkip
    })
  }

  txtSortChange(e){
    this.setState({
      sortStr: e.target.value
    })
  }

  txtLimitChange(e){
    let inputLimit = parseInt(e.target.value);
    if (isNaN(inputLimit)){
      //inputLimit = 20
      return;
    }

    this.setState({
      limit: inputLimit
    })
  }

  btnQueryClick(){
    this.queryCollection();
  }

  btnUploadFileClick(){
    FreedbDataService.uploadDocs(this.state.db_name, this.state.col_name, this.state.uploadFile);
  }

  queryCollection(){
    let query={};
    try{
      query = JSON.parse(this.state.queryStr);
    }
    catch(SyntaxError){
      query = {}
    }
    FreedbDataService.queryCollection(this.state.db_name, this.state.col_name, query,
        this.state.skip, this.state.sortStr, this.state.limit)
        .then(response=>{
          this.setState({
            docs: response.data.data,
            paging: response.data.paging,
            total_rows: response.data.paging.total,
            rows_count: response.data.paging.rows
          })
        }).catch(e=>{
      console.log(e);
    });
  }

  render() {
    const {docs, showImportDataDialog} = this.state;

    const previousSkip = Math.max(this.state.skip - this.state.limit, 0);
    const hasPreviousPage = this.state.skip > 0;
    const hasNextPage = this.state.skip + this.state.limit < this.state.total_rows;
    const nextPageSkip = this.state.skip + this.state.limit;

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
          <Button variant="outline-dark" onClick={this.btnImportDataClick}>Import</Button>
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
              <FormControl id="query" value={this.state.queryStr} onChange={this.textQueryChange} />
              <InputGroup.Append>
                <Button onClick={this.btnQueryClick}>Go</Button>
              </InputGroup.Append>
            </InputGroup>
            <InputGroup className="my-inline-group">
              <InputGroup.Prepend>
                <InputGroup.Text>Sort</InputGroup.Text>
              </InputGroup.Prepend>
              <FormControl id="sort" value={this.state.sortStr} onChange={this.txtSortChange} />
            </InputGroup>
            <InputGroup className="my-inline-group">
              <InputGroup.Prepend>
                <InputGroup.Text>Skip</InputGroup.Text>
              </InputGroup.Prepend>
              <FormControl id="skip" value={this.state.skip} type="number" onChange={this.txtSkipChange} />
            </InputGroup>
            <InputGroup className="my-inline-group">
              <InputGroup.Prepend>
                <InputGroup.Text>Limit</InputGroup.Text>
              </InputGroup.Prepend>
              <FormControl id="limit" defaultValue={this.state.limit} type="number" onChange={this.txtLimitChange} />
            </InputGroup>
          </Form.Row>
        </Form>
      </Fragment>
      <Breadcrumb>
        {this.state.skip+1}-{this.state.skip+this.state.rows_count} of {this.state.total_rows}
        {hasPreviousPage &&
          <Link to={`?skip=${previousSkip}`} className='btn btn-outline-dark'>Previous</Link>
        }

        {hasNextPage &&
          <Link to={{
            search: `?skip=${nextPageSkip}`,
          }} className='btn btn-outline-dark'>Next</Link>
        }
      </Breadcrumb>
      {docs &&
      docs.map((doc, index) => (
          <Card key={doc.id}>
            <Card.Body>
            <pre>
              {JSON.stringify(doc, undefined, 2)}</pre>
            </Card.Body>
          </Card>
      ))}
      <Modal show={showImportDataDialog} onHide={()=>this.setState({showImportDataDialog:false})}>
        <Modal.Header closeButton>
          <Modal.Title>Import Data</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.File id="uploadFile" onChange={(e)=>this.setState({uploadFile:e.target.files[0]})}></Form.File>
            </Form.Group>
          </Form>
          <p>Select data file first.</p>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={()=>this.setState({showImportDataDialog:false})}>Close</Button>
          <Button variant="primary" onClick={this.btnUploadFileClick}>Save changes</Button>
        </Modal.Footer>
      </Modal>
    </div>
  }
}
