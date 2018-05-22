import React from 'react';

import Item from './Item';

import './css/Items.css';

export default class Items extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeItem: null,
    };
  }

  render() {
    const dirs = this.props.dirs;
    const files = this.props.files;
    const items = dirs.concat(files).map(item => {
      return (
        <Item key={item.path} item={item}
          onClick={this.onItemClicked}
        />
      );
    });
    return (
      <div className="items" onClick={this.onClick}>
        {items}
      </div>
    );
  }

  onClick = () => {
    const activeItem = this.state.activeItem;
    if (activeItem) {
      activeItem.deactivate();
      this.setActiveItem(null);
    }
  }

  onItemClicked = (item) => {
    if (item === this.state.activeItem) {
      this.setActiveItem(null);
      this.props.onEnterDir(item.getItem());
    } else {
      this.activateItem(item);
    }
  }

  activateItem = (item) => {
    const activeItem = this.state.activeItem;
    if (activeItem) {
      activeItem.deactivate();
    }
    item.activate();
    this.setActiveItem(item);
  }

  setActiveItem = (item) => {
    this.setState({
      activeItem: item,
    });
    this.props.onActiveItemChanged(item && item.getItem());
  }
}
