import React from 'react';

import Nav from './Nav';
import Content from './Content';
import ItemPanel from './ItemPanel';
import Pather from './Pather';
import UserPanel from './UserPanel';

import './css/Explorer.css';

export default class Explorer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activePath: this.props.activePath || this.props.rootPath,
      activeItem: null,
    };
  }

  render() {
    return (
      <div className="explorer">
        <div className="header horizontal">
          <Pather path={this.state.activePath}/>
          <UserPanel/>
        </div>
        <div className="main horizontal">
          <Nav path={this.props.rootPath}
            activePath={this.state.activePath}
            onActivePathChanged={this.onActivePathChanged}
          />
          <Content path={this.state.activePath}
            onPathChanged={this.onActivePathChanged}
            onActiveItemChanged={this.onActiveItemChanged}
          />
          <ItemPanel item={this.state.activeItem}/>
        </div>
      </div>
    );
  }

  onActivePathChanged = (path) => {
    this.setState({activePath: path});
  }

  onActiveItemChanged = (item) => {
    this.setState({activeItem: item});
  }
}
