import 'react-hot-loader/patch';
import React from 'react';
//import {hot} from 'react-hot-loader';
//import { AppContainer } from 'react-hot-loader';
import ReactDOM from 'react-dom';
import RouterApp from './router.js';
import './css/index.css';

const render = Component => {
  ReactDOM.render(
      <Component />,
    document.getElementById('root')
  );
}

render(RouterApp);

//if (module.hot) {
//	module.hot.accept('./router.js', () => {
//	const NextRootContainer = require('./router.js').default;
//	render(<NextRootContainer />, document.getElementById('root'));
//	})
//}
