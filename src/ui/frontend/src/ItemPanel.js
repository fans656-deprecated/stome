import React from 'react';

import ItemDetail from './ItemDetail';
import ItemActions from './ItemActions';

import './css/ItemPanel.css'

export default class ItemPanel extends React.Component {
  render() {
    const node = this.props.node;
    if (!node) {
      return null;
    }
    return (
      <div className="item-panel vertical">
        <ItemDetail node={this.props.node}/>
        <div className="bottom" style={{background: '#555'}}>
          <ItemActions node={this.props.node}/>
        </div>
      </div>
    );
  }
}
