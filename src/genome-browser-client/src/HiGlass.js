import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import ReactTable from 'react-table';
import selectTableHOC from 'react-table/lib/hoc/selectTable';
import Sidebar from "react-sidebar";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import Form from 'react-bootstrap/Form';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Dropdown from 'react-bootstrap/Dropdown';
import 'react-table/react-table.css';
import CheckboxTable from './CheckboxTable.js';
import axios from 'axios';
import axiosTiming from 'axios-timing';
import ListGroup from 'react-bootstrap/ListGroup';
import SeqViewTemplate from './SeqViewTemplate.js';
import Config from 'Config';

class HiGlass extends React.Component {
	constructor(props){
		super(props);
		let filters = this.props.annotationFilters;
		filters['higlass_UID']=(function() { return function(row){return row['higlass_UID']}})();
		props.setAnnotationFilters(filters);
		this.state={
			trackPositionSelected: 'top',
			showHiglassAlert: false,
		}
	}

	getEmptyViewConfig()
	{
		
		let viewConfig = JSON.parse(JSON.stringify(this.props.config.HiGlassEmptyViewConfig)) //Copy javascript object by value instead of setting reference
		return viewConfig
	}

	constructBrowser(el){
			el.style.height="1000px";
			el.style.width="1000px";
			let viewConfig = this.getEmptyViewConfig()
			this.setState((state, props) =>{
				let hgApi = window.hglib.viewer(el,
						viewConfig,
							{ bounded: true },
				);
				return {hgApi: hgApi}
				});			
		}

	addTrackToConfig(viewConfig,tilesetUID, name, position){
		let newViewConfig = viewConfig;
		let newTrack;
		if(position.toLowerCase() == 'center'){

			newTrack = JSON.parse(JSON.stringify(this.props.config.HiGlassNewTrackCenter)) //Copy javascript object by value instead of setting reference
			newTrack.contents[0].tilesetUid = tilesetUID
			newTrack.contents[0].name = name
		}
		else{
			let orientation;
			if(position.toLowerCase() === "top" || position.toLowerCase() === "bottom"){
				orientation = "horizontal"
			}
			else{
				orientation = "vertical"
			}
				
			newTrack = JSON.parse(JSON.stringify(this.props.config.HiGlassNewTrack)) //Copy javascript object by value instead of setting reference
			newTrack.tilesetUid = tilesetUID
			newTrack.options.name = name
			newTrack.type = orientation + "-line"
		}
		newViewConfig["views"][0]["tracks"][position.toLowerCase()].push(newTrack);
		return newViewConfig
	}

	addAnnotationToConfig(viewConfig,tilesetUID, position){
		let newViewConfig = viewConfig;
		let newTrack;
		let orientation;
		position = position.toLowerCase()
		if(position == "center"){
			newViewConfig = this.addAnnotationToConfig(newViewConfig, tilesetUID, 'left')
			return this.addAnnotationToConfig(newViewConfig, tilesetUID, 'top')
		}
		if(position == "top" || position == "bottom"){
			orientation = "horizontal"
		}
		else{
			orientation = "vertical"
		}

		newTrack = JSON.parse(JSON.stringify(this.props.config.HiGlassNewAnnotationTrack)) //Copy javascript object by value instead of setting reference
		newTrack.tilesetUid = tilesetUID
		newTrack.type = orientation + "-gene-annotations"
		newViewConfig["views"][0]["genomePositionSearchBox"]["autocompleteId"] = tilesetUID; 
		newViewConfig["views"][0]["tracks"][position.toLowerCase()].push(newTrack);
		return newViewConfig;
	}
	
	isViewConfigEmpty(viewConfig){
		for(const position of ['top', 'bottom', 'center', 'left', 'right']){
			if(Object.entries(viewConfig["views"][0]["tracks"][position]).length !== 0){
				return false
			}
		}
		return true;
	}

	addTracks(state, el){
		//this.setState({showHiglassAlert: true})
		//return 0;
		let selection = this.props.selection;
		let annotationSelection = this.props.annotationSelection;
		let viewConfig = this.state.hgApi.getViewConfig();
		let newViewConfig = viewConfig;
		let select_id;
		let id;
		let row;
		let higlassfile;
		let higlassfiles;
		let autoAddAnnotations
		let strand
		let strands
		if(newViewConfig["views"][0]["genomePositionSearchBox"]["chromInfoId"] !== this.props.assemblySelected){
			newViewConfig = this.getEmptyViewConfig()	
		}
		autoAddAnnotations = this.isViewConfigEmpty(newViewConfig)
		newViewConfig["views"][0]["genomePositionSearchBox"]["autocompleteServer"] = Config.serverUrl + "/api/v1"
		newViewConfig["views"][0]["genomePositionSearchBox"]["visible"]=true;
		newViewConfig["views"][0]["genomePositionSearchBox"]["chromInfoId"]=this.props.assemblySelected;
		newViewConfig["views"][0]["genomePositionSearchBoxVisible"] = true

		const annotationRow = this.props.assemblyAnnotations.find((element)=>{return element['name']==="RefSeq Genes";})
		if(autoAddAnnotations == true && annotationSelection.length == 0){
			newViewConfig = this.addAnnotationToConfig(newViewConfig, annotationRow['higlass_UID'],this.state.trackPositionSelected)
			autoAddAnnotations = false
		}
		for (select_id of selection){
			id = select_id.replace(/^select-/, '');
			row = this.props.data.find((element)=>{return element['id']==id;})
			strands=["PlusStrand", "MinusStrand"]
			if(state.radioSelection.includes(select_id) || ['ATACSEQ', 'CHIAPET', 'DNASEQ', 'MAP', 'MNASESEQ', 'MNCHIPSEQ', 'HIC', 'STARRSEQ'].includes(row['expttype'])){
				strands = ['']
			}
			for (strand of strands){
				newViewConfig = this.addTrackToConfig(newViewConfig, id + strand, row['lab'] + "," + row['exptcondition'] + "," + row['expttarget'] + "," + row['replicate'], this.state.trackPositionSelected)
			}
		}
			

		this.state.hgApi.setViewConfig(
			newViewConfig,
		);
		}

	onTrackPositionChange(trackPosition){
		let hideAnnotations = false;
		let filters = this.props.filters;
		if(this.state.trackPositionSelected ==="Center"){
			delete filters.expttype
		}
		if(trackPosition==="Center"){
			delete filters.expttype
			filters['expttype']=(function() { return function(row){return row['expttype'].toLowerCase() === 'hic'}})();
		}

		this.props.setFilters(filters);
		this.props.setHideAnnotations(hideAnnotations);
		this.setState(function(prevState, props){
				return {trackPositionSelected: trackPosition}
		})
	}

	handleAlertClose(){
		this.setState({showHiglassAlert: false})
	}

	render(){
			let afterDropdowns= <Form.Group controlId="formTrackPosition" onChange={(e) => this.onTrackPositionChange(e.target.value)}>
					<Form.Label>Track Position:</Form.Label>
					<Form.Control as="select" >
						<option>Top</option>
						<option>Bottom</option>
						<option>Left</option>
						<option>Right</option>
						<option>Center</option>
					</Form.Control>
				</Form.Group>

	
		return(
			<SeqViewTemplate {...this.props} constructBrowser={(el) => this.constructBrowser(el)} 
						addTracks={(state, el) => this.addTracks(state, el)} afterDropdowns={afterDropdowns} showAlert={this.state.showHiglassAlert} genericAlert={"HiGlass is currently not supported. Please use IGV instead."}
handleAlertClose={()=>this.handleAlertClose()}/>
		)
	}
}

export default HiGlass;
