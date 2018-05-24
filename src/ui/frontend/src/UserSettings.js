import React from 'react';

import {Tabs, Tab} from './Tabs';

export default class UserSettings extends React.Component {
  render() {
    return (
      <div className="user-settings">
        <Tabs>
          <Tab>
            <h1>Storage</h1>
          </Tab>
          <Tab>
            <h1>Other</h1>
          </Tab>
        </Tabs>
      </div>
    );
  }
}
