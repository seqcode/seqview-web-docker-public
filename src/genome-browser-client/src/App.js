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
import './css/App.css';
import CheckboxTable from './CheckboxTable.js';
import axios from 'axios';
import axiosTiming from 'axios-timing';
import ListGroup from 'react-bootstrap/ListGroup';
import ToggleButton from 'react-bootstrap/ToggleButton';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import config from './config.js';

const filterFunctions = { 
	exact:	(filter, row, caseFunction) => caseFunction(String(row[filter.id])) === caseFunction(filter.value),
	substring:	(filter, row, caseFunction) => caseFunction(String(row[filter.id])).includes(caseFunction(filter.value)) 
}

function withApp(Browser){
	return class extends React.Component {


	constructor(props) {
		super(props);
		this.state = {
			docked: true,
			selection: [],
			radioSelection: [],
			annotationSelection: [],
			annotationFilters: [],
			selectAll: false,
			speciesSelected: "",
			assemblySelected: "",
			trackPositionSelected: "",
			hideAnnotations: false,
			assemblyTracks: [],
			assemblyAnnotations: [],
			data: [],
			assembliesData: [],
			assemblies: [],
			speciesList: {},
			annotationsList: [],
			hideTabs: "inline",
			hideTable: "inline",
			hidePeaks: "none",
			displayModal: false,
			caseSensitiveSearch: false,
			caseFunction: function(value){ return value.toUpperCase()},
			selectedFiles: "",
			settingsComponent: null,
			loaded: false,
			infoButtonLabel: "Info",
			config: config,
			exactMatch: false,
			filters: {},
			columnsNotSelected: [],
			columns: [{
			id: 'id',
			Header: 'id',
			accessor: 'id',
		}, {
			Header: 'expttype',
			accessor: 'expttype',
		}, {
			Header: 'lab',
			accessor: 'lab',
		}, {
			Header: 'expttarget',
			accessor: 'expttarget',
		}, {
			Header: 'exptcondition',
			accessor: 'exptcondition',	 
		}, {
			Header: 'cellline',
			accessor: 'cellline',		
		}, {
			Header: 'alignment',
			accessor: 'alignment',	 
		}, {
			Header: 'replicate',
			accessor: 'replicate',	 
		},
		],

 
		};

		this.state.defaultFilterMethod = (filter, row) => filterFunctions["substring"](filter,row,this.state.caseFunction)
		this.onSetSidebarOpen = this.onSetSidebarOpen.bind(this);
	}

	onSetSidebarOpen(open) {
		this.setState({ sidebarOpen: open });
	}

	setAssemblyTracks(tracks) {
		this.setState({assemblyTracks:tracks});
	}

	setHideAnnotations(hidden){
		this.setState({hideAnnotations:hidden});
	}

	setSelectAll(selectAll){
		this.setState({selectAll:selectAll});
	}

	componentDidMount() {
		let tracksLoaded = axios.get('/api/v1/seqalignments/').then(dataSet => {
				let assemblyTracks = [];
				let row;
				this.setState(prevState =>{
					let data = dataSet['data']
					let allColumns = Object.keys(data[0]).map((key) => {return {Header: key, accessor: key}})
					
					let columnsNotSelected = allColumns.filter(x => !this.state.columns.some(i => i.Header === x.Header && i.accessor === x.accessor))
					return {data: data, 'assemblyTracks': assemblyTracks, columnsNotSelected: columnsNotSelected}
				})
				}).catch(error =>{
				console.log(error);
			});

		let assembliesLoaded = axios.get('/api/v1/assemblies/').then(dataSet => {
				const data = dataSet['data'];
				let speciesList = {};
				let species ="";
				
				for(let ind = 0; ind < data.length; ind++){
					let speciesAssemblies = [];
					species = data[ind]['name'];
					
					if (speciesList.length == 0 || species in speciesList == false){
						data.filter(obj => obj.name === species).forEach(obj => speciesAssemblies.push(obj['version']))
						speciesList[species] = speciesAssemblies;
					}
				}
				this.setState({speciesList: speciesList, speciesSelected: dataSet['data'][0]['name'], 
					assemblies: speciesList[dataSet['data'][0]['name']], 
					assemblySelected: speciesList[dataSet['data'][0]['name']][0]})
			});

			let annotationsLoaded = axios.get('/api/v1/annotations/').then(dataSet => {
				this.setState({annotationsList: dataSet['data'], assemblyAnnotations: dataSet['data']})
			}); 
		//Create Component
		Promise.all([tracksLoaded, assembliesLoaded, annotationsLoaded]).then(values => {

				this.setState(prevState =>{
					let filters = prevState.filters;
					let annotationFilters = prevState.annotationFilters;
					let genomeFilter=(function() { return function(row){return row['genome'] === prevState.assemblySelected}})();
					filters['genome'] = genomeFilter;
					annotationFilters['genome'] = genomeFilter;
					let assemblyTracks = this.applyFilters(filters, prevState.data)
			let assemblyAnnotations = this.applyFilters(annotationFilters, prevState.annotationsList)
					return {assemblyTracks: assemblyTracks, loaded: true, assemblyAnnotations: assemblyAnnotations}
		})})

	}

	toggleRadioSelection(key, shift, row){
		
		// start off with the existing state
		let radioSelection = [...this.state.radioSelection];

		const keyIndex = radioSelection.indexOf(key);

		// check to see if the key exists
		if (keyIndex >= 0) {
			// it does exist so we will remove it using destructing
			radioSelection = [
				...radioSelection.slice(0, keyIndex),
				...radioSelection.slice(keyIndex + 1)
			];
		} else {
			// it does not exist so add it
			radioSelection.push(key);
		}
		// update the state
		this.setState({ radioSelection: radioSelection });
	}
		/**
	 * Toggle a single checkbox for select table
	 */
	toggleSelection(key, shift, row) {
		// start off with the existing state
		let selection = [...this.state.selection];

		const keyIndex = selection.indexOf(key);

		// check to see if the key exists
		if (keyIndex >= 0) {
			// it does exist so we will remove it using destructing
			selection = [
				...selection.slice(0, keyIndex),
				...selection.slice(keyIndex + 1)
			];
		} else {
			// it does not exist so add it
			selection.push(key);
		}
		// update the state
		this.setState({ selection: selection });
	};

	toggleAnnotationSelection(key, shift, row) {
		// start off with the existing state
		let selection = [...this.state.annotationSelection];
		const keyIndex = selection.indexOf(key);

		// check to see if the key exists
		if (keyIndex >= 0) {
			// it does exist so we will remove it using destructing
			selection = [
				...selection.slice(0, keyIndex),
				...selection.slice(keyIndex + 1)
			];
		} else {
			// it does not exist so add it
			selection.push(key);
		}
		// update the state
		this.setState({ annotationSelection: selection });
	};

	setColumns(columns){
		this.setState({columns: columns})
	}

	setColumnsNotSelected(columnsNotSelected){
		this.setState({columnsNotSelected: columnsNotSelected})
	}

	handleClose(){
		this.setState({displayModal: false});
	}

	handleSettingsCheckbox(evt, column){
		const checked = evt.target.checked
		this.setState((state,props) => {
			let columns = state.columns
			let item = {"Header" : column, "accessor": column}
			console.log("Checed:",checked)
			console.log(columns)
			if(checked){
				columns.push(item)
			}
			else{
				console.log(item)
				let index = columns.findIndex(x => x.Header === column && x.accessor === column)
				console.log(index)
				if(index !== -1){
					columns.splice(index,1);
				}
				console.log(columns)
			}
			return {columns: columns}
		});
	}

	handleSettingsListChange(){
	}

	handleModalSettings(){
		this.setState((state, props) => {
			if (state.hideTabs === "none"){
				return {hideTabs: "inline", hideTable: "inline", settingsComponent: null}
			}
			else {
				console.log("Data", Object.keys(state.data[0]))
				let selectedColumns = []
				for(let column in state.columns){
					selectedColumns.push(state.columns[column].accessor)
				}
				console.log("selectedColumns", selectedColumns)
				let settingsComponent = 
				<Form> {Object.keys(state.data[0]).map((column) => (
						<div key={column}>
							<Form.Check
								onChange={(evt) => this.handleSettingsCheckbox(evt, column)}
								checked={selectedColumns.includes(column)}
        						type="checkbox"
        						label={column}
      						/>
						</div>
 					 ))}
				</Form>
				//let settingsComponent = <Form>{["checkbox", "radio"].map((column)=>{<Form.Check type="checkbox" label={column}/>})}</Form>
				//settingsComponent = <Form><Form.Check type="checkbox" label="1"/></Form>
				return {hideTabs: "none", hideTable: "none", settingsComponent: settingsComponent}	
			}
		})
	}

	handleShow(){
		this.setState({displayModal : true});
	}

	handleSubmit(){
		this.setState((state, props) =>{

			return {displayModal: false, selection: [], radioSelection: [], selectAll: false, annotationSelection: []};
		});
 
	}

	handleInfo(){
		this.setState((state, props) => {
			let selectedFiles = "";
			let id;
			for (let ind in state.selection){
				id = state.selection[ind].replace(/^select-/, '');
				let row = state.data.find((element)=>{return element['id']==id;})
				selectedFiles = selectedFiles + JSON.stringify(row, null, '\t') + ",\n";
			}
			if (state.hideTable === "none"){
				return {hideTable: "inline", selectedFiles: "", infoButtonLabel: "Info"}
			}
			else{
				return {hideTable: "none", selectedFiles: selectedFiles, infoButtonLabel: "Back to Tracks"}
			}
		})
	}


	setAnnotationFilters(filters){
		this.setState(function(prevState,props){
			let assemblyAnnotations = this.applyFilters(filters, prevState.annotationsList)

			return {annotationFilters: filters, assemblyAnnotations: assemblyAnnotations}
		});
	}

	setFilters(filters){
		this.setState(function(prevState,props){
			let assemblyTracks = this.applyFilters(filters, prevState.data)

			return {filters: filters, assemblyTracks: assemblyTracks}
		});
	}

	applyFilters(filters, data) {
		let tracks = [...data];
		for(const field of Object.keys(filters)){
			tracks = this.filterRows(tracks, filters[field])
		}
		return tracks;
	}

	
	filterRows(data, filter) {
			let filteredRows = [];
			let row;
			for (let ind in data){
				row = {...(data[ind])} ;
				if (filter(row)){
					filteredRows.push(row);
				} 
			}
			return filteredRows
	}

	onSpeciesChange(species) {
		this.setState(function(prevState, props){
			let filters = prevState.filters;
			let annotationFilters = prevState.annotationFilters;
			let assemblySelected = ""
			let assemblyTracks = [];
			let assemblyAnnotations = [];
			if (prevState.speciesList[species].len != 0){
				assemblySelected = prevState.speciesList[species][0]
				let genomeFilter;
				genomeFilter = (function() { return function(row){return row['genome'] === assemblySelected}})();
				filters['genome'] = genomeFilter;
				annotationFilters['genome'] = genomeFilter;
				assemblyAnnotations = this.applyFilters(annotationFilters, prevState.annotationsList)
				assemblyTracks = this.applyFilters(filters, prevState.data)
			}
			return {speciesSelected: species, assemblies: prevState.speciesList[species], 
				assemblySelected: assemblySelected, assemblyTracks: assemblyTracks, filters: filters, assemblyAnnotations: assemblyAnnotations, annotationFilters: annotationFilters, selection: [], annotationSelection: [], selectedFiles: "", hideTable: "inline", infoButtonLabel: "Info"}
		})
	}

	handleCaseSensitiveChange(target){
		this.setState((state, props) => {
			let caseFunction
			let caseSensitiveSearch = !state.caseSensitiveSearch
			if(caseSensitiveSearch){
				caseFunction = (value) => value
			}
			else{
				caseFunction = (value) => value.toUpperCase()
			}
			let match = state.exactMatch ? "exact" : "substring"
			return {caseSensitiveSearch : caseSensitiveSearch, caseFunction : caseFunction, defaultFilterMethod : (filter,row) => filterFunctions[match](filter,row,caseFunction)}
		})
	}

	handleSearchFunctionChange(target){
		this.setState((state,props) => {
			let exactMatch
			let defaultFilterMethod
			if(target.id === 'exactmatch'){
				defaultFilterMethod=(filter,row) => filterFunctions["exact"](filter,row,state.caseFunction)
				exactMatch = true
			}
			else{
				defaultFilterMethod=(filter, row) => filterFunctions["substring"](filter,row,state.caseFunction) 
				exactMatch = false
			}
			return {exactMatch : exactMatch, defaultFilterMethod : defaultFilterMethod}
		})

	}

	onAssemblyChange(assembly) {
		this.setState(function(prevState, props){
			let filters = prevState.filters;
			let annotationFilters = prevState.annotationFilters;
			//filters['genome'] = function(row) {row['genome']===assembly};
			let genomeFilter = (function() { return function(row){return row['genome'] === assembly}})(); 
			filters['genome'] = genomeFilter;
			annotationFilters['genome'] = genomeFilter;
			let assemblyAnnotations = this.applyFilters(annotationFilters, prevState.annotationsList)
			let assemblyTracks = this.applyFilters(filters, prevState.data)
			return {assemblySelected: assembly, assemblyTracks: assemblyTracks, filters: filters, assemblyAnnotations: assemblyAnnotations, annotationFilters: annotationFilters, selection: [], annotationSelection: [], selectedFiles: "", hideTable: "inline", infoButtonLabel: "Info"}
		})
	}

		render(){
			return <Browser {...this.state} handleCaseSensitiveChange={(target) => this.handleCaseSensitiveChange(target)} handleSearchFunctionChange={(target) => this.handleSearchFunctionChange(target)} setColumns={(columns)=>this.setColumns(columns)} setColumnsNotSelected={(columnsNotSelected)=>this.setColumnsNotSelected(columnsNotSelected)} handleShow={()=>this.handleShow()} handleModalSettings={()=>this.handleModalSettings()} handleClose={()=>this.handleClose()} filtered={this.state.filters}
				handleInfo={()=>this.handleInfo()} filterRows={(data,filter)=>this.filterRows(data, filter)} handleSubmit={()=>this.handleSubmit()}
				toggleSelection={(key, shift, row) => this.toggleSelection(key, shift, row)}
				toggleRadioSelection={(key, shift, row) => this.toggleRadioSelection(key, shift, row)}
				toggleAnnotationSelection={(key, shift, row) => this.toggleAnnotationSelection(key, shift, row)}
				setAssemblyTracks={(assemblyTracks)=>this.setAssemblyTracks(assemblyTracks)}
				setHideAnnotations={(hidden)=>this.setHideAnnotations(hidden)}
				onSpeciesChange={(species)=>this.onSpeciesChange(species)} onAssemblyChange={(assembly)=>this.onAssemblyChange(assembly)}
				setFilters={(filters)=>this.setFilters(filters)}
		setAnnotationFilters={(filters)=>this.setAnnotationFilters(filters)}/>;
		}
	}
}

export default withApp;
