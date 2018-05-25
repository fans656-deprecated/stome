import React from 'react';

import {Tabs, Tab} from './Tabs';
import { fetchJSON } from './util';
import Edit from './Edit';

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
      'storage-templates': true
    });
    this.setState({templates: templates});
  }

  render() {
    const tabs = this.state.storages.map((i, storage) => (
      <Tab name="foo" key={i}>
        <Storage storage={storage}/>
      </Tab>
    ));
    tabs.push((
      <Tab name="+" key="new">
        <NewStorage templates={this.state.templates}
          onChange={this.populate}
        />
      </Tab>
    ));
    return (
      <div style={{minWidth: '40em', minHeight: '20em'}}>
        <Tabs direction="left">
          {tabs}
        </Tabs>
      </div>
    );
  }
}

class Storage extends React.Component {
  render() {
    return <p>storage instance</p>
  }
}

class NewStorage extends React.Component {
  edits = {}

  render() {
    const tabs = this.props.templates.map((template, i) => {
      template = Object.assign({}, template);
      let EditComponent = EditStorage;
      if (template.type === 'local') {
        EditComponent = EditStorageLocal;
      } else {
        EditComponent = EditStorageQiniu;
      }
      return (
        <Tab name={template.type} key={template.type}>
          <div>
            <EditComponent storage={template}
              ref={ref => this.edits[i] = ref}
            />
          </div>
          <div style={{marginTop: '1em'}}>
            <button onClick={this.addStorage}>Create</button>
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

  addStorage = () => {
    const tabIndex = this.tabs.index();
    const storageEdit = this.edits[tabIndex];
    console.log(storageEdit.getStorage());
  }
}

class EditStorage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      storage: props.storage,
    };
  }

  render() {
    const storage = this.state.storage;
    let fields = this.fields || this.makeFields(storage);
    return (
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
