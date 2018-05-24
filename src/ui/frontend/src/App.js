import React from 'react';
import { withRouter } from 'react-router-dom';
import Explorer from './Explorer';

class App extends React.Component {
  render() {
    return (
      <Explorer rootPath={'/'} currentPath={this.props.location.pathname}/>
    );
  }
}

App = withRouter(App);  // in order to have App.props.history

export default App;
