import React from 'react';

import Items from './Items';
import { fetchDir } from './util';

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
    const res = await fetchDir(path);
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
          onEnterDir={this.onEnterDir}
          onActiveItemChanged={this.props.onActiveItemChanged}
        />
      </div>
    );
  }

  onEnterDir = (dir) => {
    this.props.onActiveItemChanged(dir);
    this.props.onActiveDirChanged(dir);
  }
}
