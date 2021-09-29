import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import ReactTable from 'react-table';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import ToggleButton from "react-bootstrap/ToggleButton";
import Modal from "react-bootstrap/Modal";
import Form from 'react-bootstrap/Form';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-json';
import 'react-table/react-table.css';
import radioTableHOC from './RadioTable.js';
import selectTableHOC from './selectTable.js';
import checkboxTableHOC from './CheckboxTable.js';
import ColumnSettings from './ColumnSettings.js';

function setRadioValue(){
	return {}
}

const annotationColumns = [{
		id: 'id',
		Header: 'id',
		accessor: 'id',
	},{
		Header: 'Name',
		accessor: 'name',
	},{
		Header: 'File Format',
		accessor: 'fileformat',
}]
let options={floatingLeft : true}
const AnnotationTable = checkboxTableHOC(selectTableHOC(ReactTable))
const TrackTable = checkboxTableHOC(selectTableHOC(radioTableHOC(selectTableHOC(ReactTable, options))));

class ModalTracks extends React.Component {
	constructor(props){
		super(props);
		this.state={
			activeKey: 'tracks',
			checked: false,
		}
		this.modalTracks = React.createRef()
	}

	onChange(target){
		if(target.id === 'substringmatch'){
			this.setState({checked: true})
		}
	}

	setKey(k){
		this.setState({activeKey: k})
	}

	render(){

			return(
				<Modal dialogClassName="modal-90w" show={this.props.displayModal} onHide={() => this.props.handleClose()}>
				<Modal.Header closeButton>
					<Modal.Title>Add Tracks</Modal.Title>
				</Modal.Header>
				<Modal.Body>
				<Tabs activeKey={this.state.activeKey} onSelect={k => this.setKey(k)}>
					<Tab eventKey="tracks" title="Tracks" >
						<TrackTable ref={this.modalTracks} data={this.props.assemblyTracks} style={{display: this.props.hideTable}} filterable
						defaultFilterMethod={this.props.defaultFilterMethod} 
						columns={this.props.columns} keyField="id" toggleRadioSelection={this.props.toggleRadioSelection} radioSelection={this.props.radioSelection} toggleSelection={this.props.toggleSelection} selection={this.props.selection}
						selectAll={this.props.selectAll}/>
						<div><pre style={{whiteSpace: "pre-wrap", wordBreak: "break-all"}}>{this.props.selectedFiles}</pre></div>	
						<div>
							<Container>
								<Row>
									<Col>
										<Button variant="secondary mr-auto" onClick={this.props.handleInfo}>
											{this.props.infoButtonLabel}
										</Button>					
									</Col>
									<Col>
										<div className="text-right" style={{display: this.props.hidePeaks}}>
											<Form.Check type="checkbox" label="Add corresponding called Peaks" />
										</div>
									</Col>
								</Row>
							</Container>
						</div>
					</Tab>
					<Tab eventKey="annotations" title="Annotations" disabled={this.props.hideAnnotations}>
						<AnnotationTable radioSelection={this.props.radioSelection} toggleRadioSelection={this.props.toggleRadioSelection} data={this.props.assemblyAnnotations} filterable
						defaultFilterMethod={(filter, row) => String(row[filter.id]).toUpperCase().includes(filter.value.toUpperCase())} 
						columns={annotationColumns} keyField="id" toggleSelection={this.props.toggleAnnotationSelection} selection={this.props.annotationSelection}
						selectAll={this.props.selectAll}/>
					</Tab>
					<Tab eventKey="settings" title="Settings">
						<Tabs>
							<Tab eventKey="columnheaders" title="Columns Shown">
								<ColumnSettings {...this.props} leftColHeader="Available Metadata: " rightColHeader="Columns Shown: "/>
							</Tab>
							<Tab eventKey="searchsettings" title="Search Settings">
								<Form className="alignItemsRight" style={{marginTop: "20px", marginLeft: "20px"}}>
									<Form.Group as={Row}>
										<Form.Label column sm={2}>
											Search Function
										</Form.Label>
										<Col sm={10}>
											<Form.Check id='exactmatch' type='radio' label='Exact' checked={this.props.exactMatch} onChange={(evt) => this.props.handleSearchFunctionChange(evt.target)}/>
											<Form.Check id='substringmatch' type='radio' label='Anywhere in word' checked={!this.props.exactMatch} onChange={(evt) => this.props.handleSearchFunctionChange(evt.target)}/>
										</Col>
									</Form.Group>
									<Form.Group as={Row}>
										<Form.Label column sm={2}>
											Case sensitive
										</Form.Label>
										<Col sm={10}>
											<Form.Check id='casesensitive' type='checkbox' checked={this.props.caseSensitiveSearch} onChange={(evt) => this.props.handleCaseSensitiveChange(evt.target)}/>
										</Col>
									</Form.Group>
								</Form>

							</Tab>
						</Tabs>
					</Tab>
					{this.props.extraTabs}
				</Tabs>
				</Modal.Body>
				<Modal.Footer>
					<Button variant="secondary" onClick={this.props.handleClose}>
					Close
					</Button>
					<Button variant="primary" onClick={() => this.props.handleSubmit()}>
					Submit
					</Button>
				</Modal.Footer>
				</Modal>

				)
	}
}

export default ModalTracks;
