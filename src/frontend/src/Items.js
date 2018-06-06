import React from 'react';

import Item from './Item';

import './css/Items.css';

export default class Items extends React.Component {
  render() {
    const dirs = this.props.dirs;
    const files = this.props.files;
    const nodes = dirs.concat(files)
      .filter(c => !c.hidden)
      .map(node => {
        return (
          <Item key={node.meta.path} node={node}
            onClick={this.props.onClick}
          />
        );
      });
    return (
      <div className="items">
        {nodes}
      </div>
    );
  }
}
