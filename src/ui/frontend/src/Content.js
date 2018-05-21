import React from 'react';

import Items from './Items';
import { getListDirectoryResults } from './util';

export default class Content extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      dirs: [],
      files: [],
    };
  }

  async componentDidMount() {
    this.populate(this.props.path);
  }

  async componentWillReceiveProps({path}) {
    this.populate(path);
  }

  populate = async (path) => {
    const res = await getListDirectoryResults(path);
    this.setState({
      dirs: res.dirs,
      files: res.files,
    });
  }

  render() {
    return (
      <div className="content">
        <Items
          dirs={this.state.dirs}
          files={this.state.files}
          onPathChanged={this.props.onPathChanged}
          onActiveItemChanged={this.props.onActiveItemChanged}
        />
      </div>
    );
  }
}
