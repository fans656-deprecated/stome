import React from 'react';
import { Link, withRouter } from 'react-router-dom';
import Explorer from './Explorer';

class App extends React.Component {
  render() {
    return (
      <div>
        <button onClick={() => this.props.history.push('/')}>Root</button>
        <button onClick={() => this.props.history.push('/home')}>Home</button>
        <button onClick={() => this.props.history.push('/home/fans656')}>fans656</button>
        <Explorer rootPath={'/'} currentPath={this.props.location.pathname}/>
      </div>
    );
  }
}

App = withRouter(App);  // in order to have App.props.history

export default App;
