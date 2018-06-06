import React from 'react';

import {Tabs, Tab} from './Tabs';
import StorageSettings from './StorageSettings';

export default class UserSettings extends React.Component {
  render() {
    return (
      <div className="user-settings">
        <Tabs>
          <Tab name="Storage">
            <StorageSettings/>
          </Tab>
          <Tab name="Other">
            {null}
          </Tab>
        </Tabs>
      </div>
    );
  }
}
