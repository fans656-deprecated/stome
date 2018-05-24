import React from 'react';
import showDialog from './dialog';
import ManageStorage from './ManageStorage';

export default class ItemActions extends React.Component {
  render() {
    return (
      <div className="item-actions">
        <button onClick={this.onStorageClicked}>Storage</button>
      </div>
    );
  }

  onStorageClicked = () => {
    showDialog(
      <ManageStorage item={this.props.item}/>
    );
  }
}
