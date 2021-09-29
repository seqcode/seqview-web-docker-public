import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import ReactTable from 'react-table';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import Alert from 'react-bootstrap/Alert';
import GenomeTrackSidebar from "./GenomeTrackSidebar.js";
import ModalTracks from "./ModalTracks.js";

class SeqViewTemplate extends React.Component{
	static defaultProps = {
		showAlert: false,
		genericAlert: "",
		keyField: "id",
		browserClassName: "container-fluid",
		constructBrowser: function(el){},
		addTracks: function(state, el){},
		updateBrowserGenome: function(el){},
		handleAlertClose: function(state, el){},
		afterDropdowns: <div/>,
		extraTabs: <div/>,
	};

	componentDidMount(){
		this.props.constructBrowser(this.el);
	}

	handleSubmit(){
		this.props.addTracks(this.props, this.el)
		this.props.handleSubmit()
	}

	onSpeciesChange(e){
		this.props.onSpeciesChange(e)
		let assemblySelected = this.props.speciesList[e][0]
		console.log("Here")
		this.props.updateBrowserGenome(assemblySelected)
	}

	onAssemblyChange(e){
		this.props.onAssemblyChange(e)
		this.props.updateBrowserGenome(e)
	}

	render() {
		let options = { bounded: true }

	return (
		<div>
			<GenomeTrackSidebar afterDropdowns={this.props.afterDropdowns} onSpeciesChange={(e) => this.onSpeciesChange(e)} speciesList={this.props.speciesList}
				onAssemblyChange={(e) => this.onAssemblyChange(e)} assemblySelected={this.props.assemblySelected}
				assemblies = {this.props.assemblies} handleShow={()=>this.props.handleShow()} docked = {this.props.docked}
				onTrackPositionChange={(e) => this.props.onTrackPositionChange(e)} trackPositionSelected={this.props.trackPositionSelected}
			>

				<div>
					<div	ref={el => this.el = el}/>
				</div>
			</GenomeTrackSidebar>
			<Modal show={this.props.showAlert} onHide={() => this.props.handleAlertClose()}>
				<Modal.Header closeButton>
					<Alert variant="primary" show={this.props.showAlert}>{this.props.genericAlert}</Alert>
				</Modal.Header>
			</Modal>
			<ModalTracks {...this.props} displayModal={this.props.displayModal} handleClose={()=>this.props.handleClose()}
				assemblyTracks={this.props.assemblyTracks} hideTable={this.props.hideTable} hideAnnotations={this.props.hideAnnotations}
				toggleSelection={this.props.toggleSelection} selection={this.props.selection} selectedFiles={this.props.selectedFiles}
				selectAll={this.props.selectAll} annotationsList={this.props.annotationsList} handleInfo={() => this.props.handleInfo()}
				handleClose={() => this.props.handleClose()} handleSubmit={() => this.handleSubmit()} 
				toggleAnnotationSelection={this.props.toggleAnnotationSelection} annotationSelection={this.props.annotationSelection}>
			</ModalTracks>
		</div>
	);
	}
}


export default SeqViewTemplate;
