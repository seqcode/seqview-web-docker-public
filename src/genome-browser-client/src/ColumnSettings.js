// From https://codesandbox.io/s/ql08j35j3q?file=/index.js
import React, { Component } from 'react';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ReactDOM from 'react-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

// fake data generator
const getItems = (count, offset = 0) =>
    Array.from({ length: count }, (v, k) => k).map(k => ({
        id: `item-${k + offset}`,
        content: `item ${k + offset}`
    }));

// a little function to help us with reordering the result
const reorder = (list, startIndex, endIndex) => {
    const result = Array.from(list);
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);

    return result;
};

/**
 * Moves an item from one list to another list.
 */
const move = (source, destination, droppableSource, droppableDestination) => {
    const sourceClone = source.slice();
    const destClone = destination.slice();
    const [removed] = sourceClone.splice(droppableSource.index, 1);

    destClone.splice(droppableDestination.index, 0, removed);

    const result = {};
    result[droppableSource.droppableId] = sourceClone;
    result[droppableDestination.droppableId] = destClone;

    return result;
};

const grid = 4;

const getItemStyle = (isDragging, draggableStyle) => ({
    // some basic styles to make the items look a bit nicer
    userSelect: 'none',
    padding: grid * 2,
    margin: `0 0 ${grid}px 0`,
	borderBottom: '1px solid lightgrey',
	//borderStyle: 'solid',
	//borderWidth: '1px',
	//borderColor: 'lightgrey',
	textAlign: 'center',
	//color: 'lightblue',
    // change background colour if dragging
    background: isDragging ? 'white' : 'white',

    // styles we need to apply on draggables
    ...draggableStyle
});

const getListStyle = isDraggingOver => ({
    background: isDraggingOver ? 'white' : 'white',
	borderStyle: 'solid',
	borderWidth: "1px",
	borderColor: 'lightgrey',
    padding: grid,
    width: 250
});

class ColumnSettings extends Component {
    state = {
        items: getItems(10),
        selected: getItems(5, 10)
    };

    /**
     * A semi-generic way to handle multiple lists. Matches
     * the IDs of the droppable container to the names of the
     * source arrays stored in the state.
     */
    id2List = {
        droppable: 'this.props.allColumns',
        droppable2: 'this.props.columns'
    };

    getList = id => this.state[this.id2List[id]];

    onDragEnd = result => {
        const { source, destination } = result;

        // dropped outside the list
        if (!destination) {
            return;
        }

        if (source.droppableId === destination.droppableId) {
			let sourceArray = this.props.columnsNotSelected.slice()
			if (source.droppableId === 'droppable2'){
				sourceArray = this.props.columns.slice()
			}
            const items = reorder(
                sourceArray,
                source.index,
                destination.index
            );

			//let state = { items };
			console.log(items)	
	
            if (source.droppableId === 'droppable2') {
                //state = { selected: items };
                this.props.setColumns(items)
            }
			else {
            	this.props.setColumnsNotSelected(items);
			}
        } else {
			let array1 = []
			let array2 = []
			if (source.droppableId === 'droppable'){
				array1 = this.props.columnsNotSelected
				array2 = this.props.columns
			}
			else{
				array1 = this.props.columns
				array2 = this.props.columnsNotSelected
			}
            const result = move(
                array1,
                array2,
                source,
                destination
            );
			console.log(result)
			this.props.setColumns(result.droppable2)
			this.props.setColumnsNotSelected(result.droppable)
        }
    };

	onDragEnd2 = result => {
		const { source, destination } = result;

		if (!destination) {
			return
		}

		let sourceArray = this.props.allColumns
		if(source.droppableId === "droppable2"){
			sourceArray = this.props.columns
		}

    	const [sourceRemoved] = sourceArray.splice(source.index, 1);
		let destinationArray = this.props.columns
		if(destination.droppableId === "droppable2"){
			destinationArray = this.props.columns
		}

		
	}

    // Normally you would want to split things out into separate components.
    // But in this example everything is just done in one place for simplicity
    render() {
		//console.log(this.props.allColumns)
		//const unSelected = this.props.allColumns.filter(x => !this.props.columns.some(i => i.Header === x.Header && i.accessor === x.accessor))
        return (
			<div style={{marginTop: "20px", marginLeft: "20px", width: "50%"}}>
			<h6> Drag and Drop to Change Columns: </h6>
            <DragDropContext onDragEnd={this.onDragEnd}>
				<Container>
				<Row>
				<Col>
				<div style={{marginTop: "10px"}}>
					<h6>{this.props.leftColHeader}</h6>
				</div>
				<div style={{marginTop: "8px"}}>
                <Droppable droppableId="droppable">
                    {(provided, snapshot) => (
                        <div
							className="text-primary"
                            ref={provided.innerRef}
                            style={getListStyle(snapshot.isDraggingOver)}>
                            {this.props.columnsNotSelected.map((item, index) => (
                                <Draggable
                                    key={item.accessor}
                                    draggableId={item.accessor}
                                    index={index}>
                                    {(provided, snapshot) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            style={getItemStyle(
                                                snapshot.isDragging,
                                                provided.draggableProps.style
                                            )}>
                                            {item.Header}
                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
				</div>
				</Col>
				<Col>
				<div style={{marginTop: "10px"}}>
				<h6>{this.props.rightColHeader}</h6>
				</div>
				<div style={{marginTop: "8px"}}>
                <Droppable droppableId="droppable2">
                    {(provided, snapshot) => (
                        <div
							className="text-primary"
                            ref={provided.innerRef}
                            style={getListStyle(snapshot.isDraggingOver)}>
                            {this.props.columns.map((item, index) => (
                                <Draggable
                                    key={item.accessor}
                                    draggableId={item.accessor}
                                    index={index}>
                                    {(provided, snapshot) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            style={getItemStyle(
                                                snapshot.isDragging,
                                                provided.draggableProps.style
                                            )}>
                                            {item.Header}
                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
				</div>
				</Col>
				</Row>
				</Container>
            </DragDropContext>
			</div>
        );
    }
}

// Put the things into the DOM
export default ColumnSettings;
