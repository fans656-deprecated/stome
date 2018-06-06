import React from 'react';
import ManageStorage from './ManageStorage';
import Dialog from './Dialog';

export default class ItemActions extends React.Component {
  //componentDidMount() {
  //  this.manageStorageDialog.show();
  //}

  render() {
    return (
      <div className="item-actions">
        <button onClick={this.onStorageClicked}>Storage</button>
        <Dialog ref={ref => this.manageStorageDialog = ref}>
          <ManageStorage node={this.props.node}/>
        </Dialog>
      </div>
    );
  }

  onStorageClicked = () => {
    this.manageStorageDialog.show();
  }
}
