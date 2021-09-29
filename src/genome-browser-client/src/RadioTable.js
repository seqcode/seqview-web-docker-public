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
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import slugid from 'slugid';
import 'react-table/react-table.css';
import CheckboxTable from './CheckboxTable.js';
import Form from 'react-bootstrap/Form';
import Tooltip from 'react-bootstrap/Tooltip';

//const SelectTable = selectTableHOC(ReactTable);

function radioTableHOC(Component, options){
	return class RTRadioTable extends React.Component{

	constructor(props) {
		super(props)
	}

  /**
   * Whether or not a row is selected for select table
   */
  isRadioSelected = (key) => {
    return this.props.radioSelection.includes(`select-${key}`);
  };

  rowFn = (state, rowInfo, column, instance) => {
    const { radioSelection } = this.props;

    return {
      onClick: (e, handleOriginal) => {

        // IMPORTANT! React-Table uses onClick internally to trigger
        // events like expanding SubComponents and pivots.
        // By default a custom 'onClick' handler will override this functionality.
        // If you want to fire the original onClick handler, call the
        // 'handleOriginal' function.
        if (handleOriginal) {
          handleOriginal();
        }
      },
      style: {
        background:
          rowInfo &&
          radioSelection.includes(`select-${rowInfo.original.id}`) &&
          "lightgreen"
      }
    };
  };

  state = {
    selectAll: false,
    radioSelection: []
  };

  render() {
	const {isSelected, toggleSelection, selection, selectType, ...rest} = this.props
    const selectAllStyle = {
      visibility: 'hidden'
    }
    const defaultSelectAllInputComponent = props => {
  return (
    <div/>
  )
}
	// Changing which tracks are marked as only single will not change the 
	// behavior of if a track is added single or as separate strands.
	// I couldn't find any way to check if a radio button in the table was
	// selected and disabled. Added merged vs separate strands is handled based
	// on expttype.
	const selectInputComponent = props => {
		let isSingleTrack=['ATACSEQ', 'CHIAPET', 'DNASEQ', 'MAP', 'MNASESEQ', 'MNCHIPSEQ', 'HIC', 'STARRSEQ'].includes(props.row.expttype)
		let message = "Merge +/- strands into single track"
		if(isSingleTrack){
			message = "Only merged +/- strands available for this expt. type"
		}
function renderTooltip(props) {
  return (
	// The show attribute is to fix a random bug with Overlay
    <Tooltip {...props} show={props.show.toString()}>
      {message}
    </Tooltip>
			);
		}
		return (
  			<OverlayTrigger
    			placement="left"
    			delay={{ show: 250, hide: 400 }}
    			overlay={renderTooltip}
  			>
			<div>	
			<input
				type={props.selectType || 'checkbox'}
				aria-label={`${props.checked ? 'Un-select':'Select'} row with id:${props.id}` }
				checked={props.checked || isSingleTrack}
				id={props.id}
				disabled={isSingleTrack}
      			onClick={e => {
        			const { shiftKey } = e
        			e.stopPropagation()
        			props.onClick(props.id, shiftKey, props.row)
      			}}
      			onChange={() => {}}
				//style={{ pointerEvents: 'none' }}
    		/>
			</div>
			</OverlayTrigger>
			)
	}
	//return (<Component {...this.props}></Component>)
    return (
      <Component
		{...rest}
		ref={r => (this.radioTable = r)}
		selectType="radio"
		selectWidth={110}
		columnHeader="Merge Strands"
		SelectInputComponent={selectInputComponent}	
		SelectAllInputComponent={defaultSelectAllInputComponent}
		selection={this.props.radioSelection}
		toggleSelection={this.props.toggleRadioSelection}
		isSelected={this.isRadioSelected}
      >
      </Component>
    );
  }
}
}

export default radioTableHOC;
