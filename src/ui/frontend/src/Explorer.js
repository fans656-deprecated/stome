import React from 'react';
import PropTypes from 'prop-types';

import Nav from './Nav';
import Content from './Content';
import ItemPanel from './ItemPanel';
import Pather from './Pather';
import UserPanel from './UserPanel';
import { fetchDir } from './util';

import './css/Explorer.css';

export default class Explorer extends React.Component {
  state = {
    currentPath: null,
    selectedItem: null,
  }

  componentDidMount = async () => {
    const dir = await fetchDir(this.props.activePath);
    this.setCurrentDir(dir);
  }

  render() {
    const currentDir = this.state.currentDir;
    if (!currentDir) {
      return null;
    }
    const currentPath = currentDir.path;
    return (
      <div className="explorer">
        <header className="horizontal">
          <Pather path={currentPath}/>
          <UserPanel/>
        </header>
        <main className="main horizontal">
          <Nav rootPath={this.props.rootPath}
            activePath={currentPath}
            onActiveDirChanged={this.setCurrentDir}
          />
          <Content path={currentPath}
            onActiveDirChanged={this.setCurrentDir}
            onActiveItemChanged={this.setSelectedItem}
          />
          <ItemPanel item={this.getActiveItem()}/>
        </main>
        <footer>
          <div>
            <span>Stome</span>
          </div>
        </footer>
      </div>
    );
  }

  getActiveItem = () => this.state.selectedItem || this.state.currentDir

  setCurrentDir = (dir) => this.setState({currentDir: dir})

  setSelectedItem = (item) => this.setState({selectedItem: item})
}

Explorer.propTypes = {
  rootPath: PropTypes.string,
  activePath: PropTypes.string,
}
