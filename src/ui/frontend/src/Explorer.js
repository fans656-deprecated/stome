import React from 'react';
import PropTypes from 'prop-types';

import Nav from './Nav';
import Content from './Content';
import ItemPanel from './ItemPanel';
import Pather from './Pather';
import UserPanel from './UserPanel';
import getRootNode from './node';
import { fetchDir } from './util';

import './css/Explorer.css';

export default class Explorer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentDir: null,
      selectedItem: null,
    }
  }

  componentWillReceiveProps(props) {
    //this.setState({currentPath: props.currentPath});
  }

  componentDidMount = async () => {
    const root = await getRootNode(this.props.rootPath);
    root.loadChildren();
    console.log(root);
    //this.setState({currentDir: );
  }

  render() {
    //console.log(this.state.currentDir);
    return null;
    return (
      <div className="explorer">
        <header className="horizontal">
          {true ? null : <Pather path={this.state.currentPath}/>}
          {true ? null : <UserPanel/>}
        </header>
        <main className="main horizontal">
          <Nav rootPath={this.props.rootPath}
            currentPath={this.state.currentPath}
            onActiveDirChanged={this.changeDir}
          />
          {true ? null : <Content path={this.state.currentPath}
            onActiveDirChanged={this.setCurrentDir}
            onActiveItemChanged={this.setSelectedItem}
          />
          }
          {true ? null : <ItemPanel item={this.getActiveItem()}/>}
        </main>
        <footer>
          <div>
            <span>Stome</span>
          </div>
        </footer>
      </div>
    );
  }

  load = (rootPath, currentPath) => {
    const root = fetchDir(this.props.rootPath, 2);
  }

  getActiveItem = () => this.state.selectedItem || this.state.currentDir

  changeDir = (dir) => {
    this.setState({
      currentDir: dir,
      currentPath: dir.path,
    });
  }

  setSelectedItem = (item) => this.setState({selectedItem: item})
}

Explorer.propTypes = {
  rootPath: PropTypes.string,
  activePath: PropTypes.string,
}
