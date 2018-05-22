import React from 'react';
import IconSettings from 'react-icons/lib/md/settings';

import UserSettings from './UserSettings';
import Dialog from './Dialog';
//import {Tabs, Tab} from './Tabs';

export default class UserPanel extends React.Component {
  render() {
    return (
      <div className="user-panel">
        <button className="icon"
          onClick={() => this.userSettingsDialog.show()}
        >
          <IconSettings size={20}/>
        </button>
        <Dialog
          ref={ref => this.userSettingsDialog = ref}
        >
          <UserSettings/>
        </Dialog>
      </div>
    );
  }
}
