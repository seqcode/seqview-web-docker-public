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

class IGV extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			genomeLoaded: false,
		}
	}

	addTracksGenomeLoaded(selection, annotationSelection, radioSelection, assembly, annotationsList, data){
		let select_id;
		let id;
		let row;
		let strands;
		let strand;
		for (select_id of annotationSelection){
			id = select_id.replace(/^select-/, '');
			row = annotationsList.find((element)=>{return element['id']==id;})
			if (row.name === 'Gencode Genes' || row.name === 'Repeat Masker'){
				this.igv.loadTrack({
					type: "annotation",
					format: row['fileformat'],
					name: row['name'],
					url: "/tracks/" + row['genome'] + row['fileformat'] + "." + row['fileext'],
					indexURL: "/tracks/" + row['genome'] + row['fileformat'] + "." + row['fileext'] + ".tbi",		
					order: Number.MAX_VALUE,
					visibilityWindow: 10000000,
				})
			}
			else {
				console.log(row)
				this.igv.loadTrack({
					type: "annotation",
					format: row['fileformat'],
					name: row['name'],
					order: Number.MAX_VALUE,
					url: "/tracks/" + row['genome'] + row['fileformat'] + "." + row['fileext'],
					visibilityWindow: 10000000,
				})
			}			
		}

		for (select_id of selection){
			id = select_id.replace(/^select-/, '');
			row = data.find((element)=>{return element['id']==id;})
			strands = ['PlusStrand', 'MinusStrand']
			if(radioSelection.includes(select_id)){
				strands = ['']
			}
			console.log(strands)
			for(strand of strands){
				this.igv.loadTrack({
					type: "wig",
					name: row['lab'] + "," + row['exptcondition'] + "," + row['expttarget'] + "," + row['replicate'] + "," + row['cellline'],
					url: "/api/v1/tracks/" + id + strand + ".bw",})
			}	
		}
	}

	addTracks(state, el){
		let selection = state.selection;
		let annotationSelection = state.annotationSelection;
		let radioSelection = state.radioSelection;
		let assembly = state.assemblySelected;
		let annotationsList = state.annotationsList;
		let data = state.data;
		this.igv = window.igv_webapp.getBrowser()
		const reference = {
					"id": assembly,
					"name": assembly,
					"fastaURL": seqviewConfig.serverUrl + "/tracks/"
												+ assembly + ".fa",
					"indexURL": seqviewConfig.serverUrl + "/tracks/" + assembly + ".fa.fai",
					};
		if(this.state.genomeLoaded){ 
			this.addTracksGenomeLoaded(selection, annotationSelection, radioSelection, assembly, annotationsList, data)
		}
		else{
			this.igv.loadGenome(reference).then(() =>
			{
				if(!annotationSelection.length){
					let row = annotationsList.find((element)=>{return element['genome']==assembly && element['name'] == "Gencode Genes";})
					if(row === undefined){
						 row = annotationsList.find((element)=>{return element['genome']==assembly && element['name'] == "RefSeq Genes";})
					}
					if(row === undefined){
						annotationSelection=[]
					}
					else{
						annotationSelection = ['select-' + row['id']]
					}
				}
				this.addTracksGenomeLoaded(selection, annotationSelection, radioSelection, assembly, annotationsList, data)
			})					
			this.setState({genomeLoaded: true});
		}
	}

	constructBrowser(el){
		window.igv_webapp.createWebApp(el)
	}


	updateBrowserGenome(assembly){
		const reference = {
					"id": assembly,
					"name": assembly,
					"fastaURL": seqviewConfig.serverUrl + "/tracks/"
												+ assembly + ".fa",
					"indexURL": seqviewConfig.serverUrl + "/tracks/" + assembly + ".fa.fai",
					};
		window.igv_webapp.setGenome(assembly).then(() => {
			this.igv = window.igv_webapp.getBrowser()
			window.igv_webapp.getBrowser().loadGenome(reference)
			})
	}

	render(){

		return(
			<SeqViewTemplate {...this.props} browserClassName="container-fluid" constructBrowser={(el) => this.constructBrowser(el)} updateBrowserGenome={(assembly) => this.updateBrowserGenome(assembly)} addTracks={(state, el) => this.addTracks(state, el)} />
			)
	}
}  

export default IGV;
