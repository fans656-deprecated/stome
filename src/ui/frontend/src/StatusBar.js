import React from 'react';
import './css/StatusBar.css';

export default class StatusBar extends React.Component {
  render() {
    const item = this.props.item;
    let text;
    if (item.meta.listable) {
      const nItems = item.children.length;
      const plural = nItems > 1;
      text = (
        <span>{nItems + ' item' + (plural ? 's' : '')}</span>
      );
    } else {
    }
    return (
      <div className="status-bar left-right">
        <div className="left">
          {text}
        </div>
        <div className="right">
          {text}
        </div>
      </div>
    );
  }
}
