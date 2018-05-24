import React from 'react';

import './css/Item.css';

import dirImg from './img/dir.png';
import fileImg from './img/file.png';

export default class Item extends React.Component {
  render() {
    const item = this.props.item;
    let icon = null;
    if (item.meta.type === 'file') {
      icon = fileImg;
    } else if (item.meta.type === 'dir') {
      icon = dirImg;
    }
    let classes = ['item'];
    if (item.isCurrentItem()) {
      classes.push('active');
    }
    return (
      <div className={classes.join(' ')} onClick={this.onClick}>
        <img className="thumbnail" src={icon} alt={item.meta.path} width={64}/>
        <span className="name">{item.meta.name}</span>
      </div>
    );
  }

  getItem = () => {
    return this.props.item;
  }

  onClick = (ev) => {
    this.props.onClick(this.props.item);
    ev.stopPropagation();
  }

  activate = () => {
    this.setState({active: true});
  }

  deactivate = () => {
    this.setState({active: false});
  }
}
