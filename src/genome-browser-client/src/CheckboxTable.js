import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import ReactTable from 'react-table';
import selectTableHOC from './selectTable.js';
//import selectTableHOC from 'react-table/lib/hoc/selectTable';
import Sidebar from "react-sidebar";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import slugid from 'slugid';
import 'react-table/react-table.css';
import radioTableHOC from './RadioTable.js';

//let options={floatingLeft : true}
//const SelectTable = selectTableHOC(radioTableHOC(selectTableHOC(ReactTable, options)));


function checkboxTableHOC(Component, options){
	return class RTCheckboxTable extends React.Component{

  /**
   * Whether or not a row is selected for select table
   */
  isSelected = key => {
    return this.props.selection.includes(`select-${key}`);
  };

  rowFn = (state, rowInfo, column, instance) => {
    const { selection } = this.props;

    return {
      onClick: (e, handleOriginal) => {
        console.log("It was in this row:", rowInfo);

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
          selection.includes(`select-${rowInfo.original.id}`) &&
          "lightgreen"
      }
    };
  };

  //state = {
  //  selectAll: false,
  //  selection: []
  //};

  render() {
    const selectAllStyle = {
      visibility: 'hidden'
    }
    const defaultSelectInputComponent = props => {
  return (
    <div/>
  )
}

	console.log("In render CheckboxTable", this.props.radioSelection)
    return (
      <Component
        {...this.props}
        ref={r => (this.checkboxTable = r)}
        selectType="checkbox"
        isSelected={this.isSelected}
        SelectAllInputComponent={defaultSelectInputComponent}
      >
      </Component>
    );
  }
}
}

export default checkboxTableHOC;
