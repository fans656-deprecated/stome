import React from 'react';

import {Tabs, Tab} from './Tabs';

export default class ManageStorage extends React.Component {
  render() {
    return (
      <div>
        <Tabs>
          <Tab name="Local">
            <p>local</p>
          </Tab>
          <Tab name="Qiniu">
            <p>qiniu</p>
          </Tab>
        </Tabs>
      </div>
    )
  }
}
