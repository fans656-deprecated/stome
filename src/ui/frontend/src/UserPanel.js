import React from 'react';
import IconSettings from 'react-icons/lib/md/settings';

import UserSettings from './UserSettings';
import Dialog from './Dialog';
import {IconButton} from './Button';

export default class UserPanel extends React.Component {
  render() {
    return (
      <div className="user-panel">
        <IconButton
          title="Settings"
          icon={IconSettings}
          onClick={this.onSettingsClicked}
        />
        <Dialog ref={ref => this.dialog = ref}>
          <UserSettings/>
        </Dialog>
      </div>
    );
  }

  onNewFolderClicked = () => {
  }

  onUploadClicked = () => {
    window.upload();
  }

  onSettingsClicked = () => {
    this.dialog.show();
  }
}
