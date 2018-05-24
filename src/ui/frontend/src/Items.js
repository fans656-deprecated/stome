import React from 'react';

import Item from './Item';

import './css/Items.css';

export default class Items extends React.Component {
  render() {
    const dirs = this.props.dirs;
    const files = this.props.files;
    const items = dirs.concat(files).map(item => {
      return (
        <Item key={item.meta.path} item={item}
          onClick={this.props.onClick}
        />
      );
    });
    return (
      <div className="items">
        {items}
      </div>
    );
  }
}
