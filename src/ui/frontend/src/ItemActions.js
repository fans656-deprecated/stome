import React from 'react';

import Dialog from './Dialog';
import ManageStorage from './ManageStorage';

export default class ItemActions extends React.Component {
  render() {
    const item = this.props.item;
    return (
      <div className="item-actions">
        <button onClick={this.onStorageClicked}>Storage</button>
        <Dialog
          ref={ref => this.storageDialog = ref}
          buttons={{
            'ok': null,
            'cancel': null,
          }}
        >
          <ManageStorage item={item}/>
        </Dialog>
      </div>
    );
  }

  onStorageClicked = () => {
    this.storageDialog.show();
  }
}
