import React from 'react';

import {Tabs, Tab} from './Tabs';
import { fetchJSON } from './util';
import Edit from './Edit';
import './css/StorageSettings.css';

export default class StorageSettings extends React.Component {
  state = {
    templates: [],
    storages: [],
  }

  componentDidMount = () => {
    this.populate();
  }

  populate = async () => {
    const {templates} = await fetchJSON('GET', '/', {
      'storage-templates': true,
    });
    const {storages} = await fetchJSON('GET', '/', {
      'storages': true,
    });
    this.setState({
      templates: templates,
      storages: storages,
    });
  }

  render() {
    const tabs = this.state.storages.map((storage, i) => (
      <Tab name={storage.name} key={i}>
        <Storage storage={storage}
          onChange={this.populate}
        />
      </Tab>
    ));
    tabs.push((
      <Tab name="New" key="new">
        <NewStorage templates={this.state.templates}
          onChange={this.populate}
        />
      </Tab>
    ));
    return (
      <div className="storage-settings">
        <Tabs direction="left">
          {tabs}
        </Tabs>
      </div>
    );
  }
}

class Storage extends React.Component {
  render() {
    const storage = this.props.storage;
    const EditComponent = getEditStorageComponent(storage);
    return (
      <div>
        <EditComponent storage={storage}
          ref={ref => this.edit = ref}
        />
        <div className="storage-buttons">
          <button onClick={this.saveStorage}>Save</button>
          <button onClick={this.deleteStorage}>Delete</button>
        </div>
      </div>
    );
  }

  saveStorage = async () => {
    const storage = this.props.storage;
    await fetchJSON('PUT', '/?storage', storage);
    this.props.onChange();
  }

  deleteStorage = async () => {
    const id = this.props.storage.id;
    await fetchJSON('DELETE', `/${id}`, {
      storage: true,
    });
    this.props.onChange();
  }
}

class NewStorage extends React.Component {
  edits = {}

  render() {
    const tabs = this.props.templates.map((template, i) => {
      template = Object.assign({}, template);
      const EditComponent = getEditStorageComponent(template);
      return (
        <Tab name={template.type} key={template.type}>
          <EditComponent storage={template}
            ref={ref => this.edits[i] = ref}
          />
          <div style={{marginTop: '1em'}}>
            <button onClick={this.createStorage}>Create</button>
          </div>
        </Tab>
      );
    });
    return (
      <Tabs ref={ref => this.tabs = ref}>
        {tabs}
      </Tabs>
    );
  }

  createStorage = async () => {
    const tabIndex = this.tabs.index();
    const storageEdit = this.edits[tabIndex];
    const storage = storageEdit.getStorage();
    await fetchJSON('PUT', '/?storage', storage);
    this.props.onChange();
  }
}

class EditStorage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      storage: props.storage,
    };
  }

  componentWillReceiveProps(props) {
    this.setState({storage: props.storage});
  }

  render() {
    const storage = this.state.storage;
    let fields = this.fields || this.makeFields(storage);
    return (
      <div>
        <div>
          {
            fields.map(({name, key}) => (
              <Edit
                key={key}
                name={name}
                value={storage[key]}
                onChange={val => {storage[key] = val; this.setState({})}}
              />
            ))
          }
        </div>
        <div>
          <pre>{JSON.stringify(storage, null, 2)}</pre>
        </div>
      </div>
    );
  }

  getStorage() {
    return this.state.storage;
  }

  makeFields = (storage) => {
    const fields = [];
    for (let key in storage) {
      fields.push({name: key, key: key});
    }
    return fields;
  }
}

class EditStorageLocal extends EditStorage {
  fields = [
    {name: 'Name', key: 'name'},
    {name: 'Root', key: 'root'},
  ]
}

class EditStorageQiniu extends EditStorage {
  fields = [
    {name: 'Name', key: 'name'},
    {name: 'Domain', key: 'domain'},
    {name: 'Bucket', key: 'bucket'},
    {name: 'Access Key', key: 'access-key'},
    {name: 'Secret Key', key: 'secret-key'},
  ]
}

function getEditStorageComponent(storage) {
  let component = EditStorage;
  if (storage.type === 'local') {
    component = EditStorageLocal;
  } else if (storage.type === 'qiniu') {
    component = EditStorageQiniu;
  } else {
    component = EditStorage;
  }
  return component;
}
