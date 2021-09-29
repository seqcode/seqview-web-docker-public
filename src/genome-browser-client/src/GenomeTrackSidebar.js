import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import Sidebar from "react-sidebar";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Image from "react-bootstrap/Image";
import Form from 'react-bootstrap/Form';
import Dropdown from 'react-bootstrap/Dropdown';
import ListGroup from 'react-bootstrap/ListGroup';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import DropdownButton from 'react-bootstrap/DropdownButton';

class GenomeTrackSidebar extends React.Component {


	render(){
	return(
	 <Sidebar
		sidebar={
		<Container>
		<ListGroup>
			<ListGroup.Item>
				<DropdownButton id="dropdown-basic-button" title={<Image src='/static/frontend/SeqViewLogoBanner.png' fluid/>} variant='link'>
					<Dropdown.Item href="/">Home</Dropdown.Item>
					<Dropdown.Divider />
					<Dropdown.Item href="/accounts/logout/">Logout</Dropdown.Item>
				</DropdownButton>
			</ListGroup.Item>
			<ListGroup.Item>
				<Form>

					<Form.Group controlId="formSpecies">
					<Form.Label>Species:</Form.Label>
						<Form.Control as="select" onChange={(e) => this.props.onSpeciesChange(e.target.value)}>
							{ 
								Object.keys(this.props.speciesList).map((item, i) =>
								<option key={i}>{item}</option>
								)
							}
						</Form.Control>
					</Form.Group>


					<Form.Group controlId="formAssembly">
					<Form.Label>Assembly:</Form.Label>
						<Form.Control as="select" onChange={(e) => this.props.onAssemblyChange(e.target.value)} value={this.props.assemblySelected}>
						{		 
							this.props.assemblies.map((item, i) =>
							<option key={i}>{item}</option>
							)
						}
						</Form.Control>
					</Form.Group>
					{this.props.afterDropdowns}
					<Button variant="primary" onClick={() => this.props.handleShow()}>Add Tracks</Button>
				</Form>
			</ListGroup.Item>
			</ListGroup>
		</Container>

		}
		docked={this.props.docked}
		styles={{ sidebar: { background: "white", width: "250px" } }}>
		{this.props.children}
	</Sidebar> 
	)  
	}
}


export default GenomeTrackSidebar;
