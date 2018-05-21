import React from 'react';
import { withRouter } from 'react-router-dom';
import Explorer from './Explorer';

class App extends React.Component {
  render() {
    return (
      <div className="main">
        <Explorer
          rootPath={'/'}
          activePath={this.props.location.pathname}
        />
      </div>
    );
  }
}

App = withRouter(App);  // in order to have App.props.history

export default App;
