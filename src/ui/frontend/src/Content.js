import React from 'react';
import IconNewFolder from 'react-icons/lib/md/create-new-folder';
import IconUpload from 'react-icons/lib/fa/upload';
import IconDelete from 'react-icons/lib/md/delete';
import IconEdit from 'react-icons/lib/ti/edit';

import Items from './Items';
import Dialog from './Dialog';
import {IconButton} from './Button';

export default class Content extends React.Component {
  render() {
    return (
      <div className="content"
        onClick={() => this.props.onClick(null)}
        onDragOver={ev => ev.preventDefault()}
        onDrop={this.onDrop}
      >
        <Items
          dirs={this.props.currentDir.dirs}
          files={this.props.currentDir.files}
          onClick={this.props.onClick}
          onMouseDown={(ev) => ev.preventDefault()}
        />
        <Panel
          item={this.props.currentItem}
          onItemChange={this.props.onItemChange}
        />
      </div>
    );
  }

  onDrop = (ev) => {
    console.log(ev);
  }
}

class Panel extends React.Component {
  render() {
    const item = this.props.item;
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <IconButton
            title="Upload"
            tabindex="1"
            icon={IconUpload}
            onClick={() => window.upload()}
          />
          <IconButton
            title="New folder"
            tabindex="2"
            icon={IconNewFolder}
            onClick={this.createDir}
          />
        </div>
        {item && <div>
          <IconButton
            title="Edit"
            icon={IconEdit}
            onClick={this.editItem}
          />
          <IconButton
            title="Delete"
            icon={IconDelete}
            onClick={this.deleteItem}
          />
        </div>}
        <Dialog ref={ref => this.dialog = ref}>
          {null}
        </Dialog>
      </div>
    );
  }

  deleteItem = async () => {
    const item = this.props.item;
    await item.delete();
    this.props.onItemChange();
  }

  createDir = () => {
    //this.props.onItemChange();
  }
}
