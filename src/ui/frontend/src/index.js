import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';

import App from './App';
import './style.css';

//import {Tabs, Tab} from './Tabs';
//class Edit extends React.Component {
//  constructor(props) {
//    super(props);
//    this.state = {
//      text: 'AWS',
//    };
//  }
//
//  getTabLabel = () => {
//  }
//
//  render() {
//    return (
//      <div>
//        <h1>{this.state.text}</h1>
//        <input value={this.state.text} onChange={({target}) => {
//          this.setState({text: target.value});
//        }}/>
//      </div>
//    );
//  }
//}
//ReactDOM.render((
//  <BrowserRouter>
//    <Tabs>
//      <Tab label="Local">
//        <p>local storage</p>
//      </Tab>
//      <Tab label="Qiniu">
//        <p>qiniu storage</p>
//      </Tab>
//      <Tab>
//        <Edit/>
//      </Tab>
//    </Tabs>
//  </BrowserRouter>
//), document.getElementById('root'));

ReactDOM.render((
  <BrowserRouter>
    <App/>
  </BrowserRouter>
), document.getElementById('root'));
