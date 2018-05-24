import React from 'react';
import IconSettings from 'react-icons/lib/md/settings';

import UserSettings from './UserSettings';
import Dialog from './dialog';

export default class UserPanel extends React.Component {
  render() {
    return (
      <div className="user-panel">
        <button className="icon" onClick={this.onSettingsClicked}>
          <IconSettings size={20}/>
        </button>
        <Dialog ref={ref => this.dialog = ref}>
          <UserSettings/>
        </Dialog>
      </div>
    );
  }

  onSettingsClicked = () => {
    this.dialog.show();
  }
}
