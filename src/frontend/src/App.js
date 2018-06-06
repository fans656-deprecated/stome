import React from 'react'
import { withRouter } from 'react-router-dom'
import qs from 'qs'

import Todo from './todo'
import Explorer from './Explorer'

class App extends React.Component {
  render() {
    const params = qs.parse(this.props.location.search.substring(1));
    if ('todo' in params) return <Todo/>;
    return (
      <Explorer rootPath={'/'} currentPath={this.props.location.pathname}/>
    );
  }
}

App = withRouter(App);  // in order to have App.props.history

export default App;
