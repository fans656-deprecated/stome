import React from 'react';

import dirImg from './img/dir.png';
import fileImg from './img/file.png';

export default class Item extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
    };
  }

  render() {
    const item = this.props.item;
    let icon = null;
    if (item.type === 'file') {
      icon = fileImg;
    } else if (item.type === 'dir') {
      icon = dirImg;
    }
    let classes = ['item'];
    if (this.state.active) {
      classes.push('active');
    }
    return (
      <div className={classes.join(' ')} onClick={this.onClick}>
        <img className="thumbnail" src={icon} alt={item.path} width={64}/>
        <span className="name">{item.name}</span>
      </div>
    );
  }

  getItem = () => {
    return this.props.item;
  }

  onClick = (ev) => {
    this.props.onClick(this);
    ev.stopPropagation();
  }

  activate = () => {
    this.setState({active: true});
  }

  deactivate = () => {
    this.setState({active: false});
  }
}
