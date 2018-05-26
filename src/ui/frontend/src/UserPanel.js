import React from 'react';
import IconSettings from 'react-icons/lib/md/settings';
import IconUpload from 'react-icons/lib/fa/upload';

import UserSettings from './UserSettings';
import Dialog from './Dialog';

export default class UserPanel extends React.Component {
  render() {
    const iconSize = 18;
    return (
      <div className="user-panel">
        <button className="icon" onClick={this.onUploadClicked}
          title="Upload"
        >
          <IconUpload size={iconSize}/>
        </button>
        <button className="icon" onClick={this.onSettingsClicked}
          title="Settings"
        >
          <IconSettings size={iconSize}/>
        </button>
        <Dialog ref={ref => this.dialog = ref}>
          <UserSettings/>
        </Dialog>
      </div>
    );
  }

  onUploadClicked = () => {
    window.upload();
  }

  onSettingsClicked = () => {
    this.dialog.show();
  }
}
