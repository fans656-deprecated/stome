import React from 'react';
import './css/StatusBar.css';

export default class StatusBar extends React.Component {
  render() {
    const item = this.props.item;
    let ret;
    if (item.meta.listable) {
      const nItems = item.children.length;
      const plural = nItems > 1;
      ret = (
        <span>{nItems + ' item' + (plural ? 's' : '')}</span>
      );
    } else {
    }
    return (
      <div className="status-bar">
        {ret}
      </div>
    );
  }
}
