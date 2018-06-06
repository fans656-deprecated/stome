import React from 'react'

import Items from './Items'
import ContentPanel from './ContentPanel'

export default class Content extends React.Component {
  constructor(props) {
    super(props);
    window.on('keyup', this.onKeyUp);
  }

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
        <ContentPanel
          item={this.props.currentItem}
          currentDir={this.props.currentDir}
          deleteItem={this.deleteItem}
          onItemChange={this.props.onItemChange}
        />
      </div>
    );
  }

  onKeyUp = (ev) => {
    if (ev.key === 'Delete') {
      this.deleteItem(this.props.currentItem);
    }
  }

  deleteItem = async (item) => {
    await item.delete();
    this.props.onItemDeleted(item);
    this.props.onItemChange();
  }
}
