import {hot} from 'react-hot-loader/root';
import React from 'react';
import ReactDOM from 'react-dom';
import './css/App.css';
import GenomeTrackSideBar from './App';
import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Jumbotron from 'react-bootstrap/Jumbotron';
import withApp from './App';
import {
	BrowserRouter as Router,
	Switch,
	Route,
	Link
} from "react-router-dom";
import HiGlass from './HiGlass.js';
import IGV from './IGV.js';



class HomePage extends React.Component{
	constructor(props){
		document.title="SeqView"
		super(props);
		this.state={
			IGVStyle: {'width': '12rem'},
			HiGlassStyle: {'width': '12rem'},
			display: 'block'
		}
	}
	// This should probably be done in pure CSS
	onIGVMouseOver(){
		this.setState({IGVStyle: {'width' :'14rem', 'transition' : '0.2s ease'}})
	}

	onIGVMouseOut(){
		this.setState({IGVStyle: {'width': '12rem', 'transition' : '0.2s ease'}})
	}
	onHiGlassMouseOver(){
		this.setState({HiGlassStyle: {'width' :'14rem', 'transition' : '0.2s ease'}})
	}

	onHiGlassMouseOut(){
		this.setState({HiGlassStyle: {'width' :'12rem', 'transition' : '0.2s ease'}})
	}

	render(){
		return (
				<Jumbotron style={{height: "700px", display: this.state.display}}>
					<Container>
						<h1> Choose a Browsing Experience: </h1>
						<Container className="d-flex justify-content-center align-items-center" style={{height: "50vh"}}>

							<Row >
								<Col>
									<Card style={this.state.IGVStyle} onMouseOver={()=>this.onIGVMouseOver()}
										onMouseOut={()=>this.onIGVMouseOut()}>						
										<Card.Body>
											<Link to="/igv">
												<Card.Img variant="top" src="./static/frontend/igv.png" alt="..." />
											</Link>
											<Card.Title>IGV</Card.Title>
										</Card.Body>
										
									</Card>
								</Col>
								<Col>
									<Card style={this.state.HiGlassStyle} onMouseOver={()=>this.onHiGlassMouseOver()}
										onMouseOut={()=>this.onHiGlassMouseOut()}>
										<Card.Body>
											<Link to="/higlass"> 
												<Card.Img variant="top" src="./static/frontend/higlass.jpg" alt="..."/>
											</Link>
											<Card.Title>HiGlass</Card.Title>
										</Card.Body>			
									</Card>
								</Col>
							</Row>

						</Container>
					</Container>
				</Jumbotron>		
		)
	}
}


class RouterApp extends React.Component {
	constructor(props){
		super(props)
	}
	
	render(){
		return(
			<Router>
		{/* A <Switch> looks through its children <Route>s and
						renders the first one that matches the current URL. */}
				<Switch >
					<Route path="/igv" >
						<BrowserIGV/>
					</Route>
					<Route path="/higlass">
						<BrowserHiGlass />
					</Route>
					<Route path="/">
						<HomePage/>
					</Route>
				</Switch>
			</Router>
		);
	}
}

const BrowserIGV = withApp(IGV);
const BrowserHiGlass = withApp(HiGlass);


export default hot(RouterApp);
