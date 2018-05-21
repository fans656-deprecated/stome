import React from 'react';

import ItemDetail from './ItemDetail';
import ItemActions from './ItemActions';

export default class ItemPanel extends React.Component {
  render() {
    const item = this.props.item;
    if (!item) {
      return null;
    }
    return (
      <div className="item-panel vertical">
        <ItemDetail item={this.props.item}/>
        <div className="bottom" style={{background: '#555'}}>
          <ItemActions item={this.props.item}/>
        </div>
      </div>
    );
  }
}
