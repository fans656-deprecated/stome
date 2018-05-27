import React from 'react'
import { withRouter } from 'react-router-dom'
import qs from 'query-string'

import Explorer from './Explorer'

const todo = [
  'directory size',
  'file thumbnail',
  'uploading progress',
  'search',
  'move/copy (drag / ctrl-c)',
  'selection rect',
  'image view',
];

class App extends React.Component {
  render() {
    const params = qs.parse(this.props.location.search);
    if ('todo' in params) {
      return (
        <div>
          <h1>TODO</h1>
          <ul>
            {todo.map(s => <li>{s}</li>)}
          </ul>
        </div>
      );
    }
    return (
      <Explorer rootPath={'/'} currentPath={this.props.location.pathname}/>
    );
  }
}

App = withRouter(App);  // in order to have App.props.history

export default App;
