import React from 'react'
import IconNewDir from 'react-icons/lib/md/create-new-folder'
import IconUpload from 'react-icons/lib/fa/upload'
import IconDelete from 'react-icons/lib/md/delete'
import IconEdit from 'react-icons/lib/ti/edit'

import { IconButton } from './Button'
import { joinPaths, newName } from './util'
import api from './api'

export default class ContentPanel extends React.Component {
  render() {
    const item = this.props.item;
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <div className="button-group">
          <IconButton
            title="Upload file"
            tabindex="1"
            icon={IconUpload}
            onClick={() => window.upload()}
          />
          <IconButton
            title="New directory"
            tabindex="2"
            icon={IconNewDir}
            onClick={this.createDir}
          />
        </div>
        {item && <div className="button-group">
          <IconButton
            title="Edit"
            icon={IconEdit}
          />
          <IconButton
            title="Delete"
            icon={IconDelete}
            onClick={() => this.props.deleteItem(this.props.item)}
          />
        </div>}
      </div>
    );
  }

  createDir = async () => {
    const dir = this.props.currentDir;
    const existedNames = dir.children.map(c => c.meta.name);
    const name = newName(existedNames)
    const path = joinPaths(dir.meta.path, name);
    await api.post(path + '?op=mkdir');
    await dir.update();
    this.props.onItemChange();
  }
}
