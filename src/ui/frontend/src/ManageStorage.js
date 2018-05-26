import React from 'react';
import {Tabs, Tab} from './Tabs';
import {fetchJSON} from './util';
import './css/ManageStorage.css';

export default class ManageStorage extends React.Component {
  state = {
    storages: [],
  }

  componentDidMount = async () => {
    const {storages} = await fetchJSON('GET', '/', {storages: true});
    this.setState({storages: storages});
  }

  render() {
    const node = this.props.node;
    const meta = node.meta;
    const ids = meta.storages || [];
    const storages = this.state.storages;
    return (
      <div className="manage-storage">
        <Tabs direction="left">
          {storages.map(storage => this.makeTab(ids, storage))}
        </Tabs>
      </div>
    )
  }

  makeTab(ids, storage) {
    const using = ids.some(id => id === storage.id);
    let tabName = storage.name;
    if (using) {
      tabName = '+ ' + tabName;
    } else {
      tabName = '- ' + tabName;
    }
    return (
      <Tab name={tabName} key={storage.id}>
        <pre>{JSON.stringify(storage, null, 2)}</pre>
        <button onClick={() => this.toggleStorage(storage, !using)}>
          {using ? 'Disable' : 'Enable'}
        </button>
      </Tab>
    );
  }

  toggleStorage = async (storage, enable) => {
    const node = this.props.node;
    const meta = node.meta;
    if (enable) {
      meta.storages.push(storage.id);
    } else {
      meta.storages = meta.storages.filter(id => id !== storage.id);
    }
    let path = meta.path;
    if (meta.listable && !path.endsWith('/')) path += '/';
    await fetchJSON('PUT', path + '?meta', {
      path: meta.path,
      storages: meta.storages,
    });
    await node.update(true);
    this.setState({});
  }
}
