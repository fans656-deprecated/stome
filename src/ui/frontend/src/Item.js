import React from 'react';

import './css/Item.css';

import dirImg from './img/dir.png';
import fileImg from './img/file.png';

export default class Item extends React.Component {
  render() {
    const node = this.props.node;
    let icon = null;
    if (node.meta.type === 'file') {
      icon = fileImg;
    } else if (node.meta.type === 'dir') {
      icon = dirImg;
    }
    let classes = ['item'];
    if (node.isCurrentItem()) {
      classes.push('active');
    }
    return (
      <div className={classes.join(' ')} onClick={this.onClick}>
        <img className="thumbnail" src={icon} alt={node.meta.path} width={64}/>
        <span className="name">{node.meta.name}</span>
      </div>
    );
  }

  getItem = () => {
    return this.props.node;
  }

  onClick = (ev) => {
    this.props.onClick(this.props.node);
    ev.stopPropagation();
  }

  activate = () => {
    this.setState({active: true});
  }

  deactivate = () => {
    this.setState({active: false});
  }
}
