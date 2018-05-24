import React from 'react';
import { withRouter } from 'react-router-dom';

import Pather from './Pather';
import UserPanel from './UserPanel';
import Nav from './Nav';
import Content from './Content';
import ItemPanel from './ItemPanel';
import StatusBar from './StatusBar';
import getTree from './node';

import './css/Explorer.css';

class Explorer extends React.Component {
  state = {
    tree: null,
  }

  componentWillReceiveProps = async (props) => {
    await this.state.tree.setCurrentPath(props.currentPath);
    this.setState({});
  }

  componentDidMount = async () => {
    const tree = await getTree(this.props.rootPath);
    await tree.setCurrentPath(this.props.currentPath);
    window.root = tree.root;
    this.setState({tree: tree});
  }

  render() {
    const tree = this.state.tree;
    if (!tree) return null;
    return (
      <div className="explorer">
        <header className="horizontal">
          <Pather path={this.state.tree.currentDir.meta.path}/>
          <UserPanel/>
        </header>
        <main className="horizontal">
          <Nav tree={this.state.tree}
            onNodeClicked={this.onNodeClickedInNav}
            onNodeToggled={this.onNodeToggledInNav}
          />
          <Content dir={this.state.tree.currentDir}
            onClick={this.onItemClickedInContent}
          />
          <ItemPanel item={tree.currentItem || tree.currentDir}/>
        </main>
        <footer>
          <StatusBar item={tree.currentItem || tree.currentDir}/>
        </footer>
      </div>
    );
  }

  onNodeClickedInNav = async (node) => {
    if (node.isCurrentDir()) {
      await node.toggle();
    } else {
      this.changeCurrentDir(node);
    }
    this.setState({});
  }

  onItemClickedInContent = async (node) => {
    if (node && node.isCurrentItem()) {
      if (node.meta.listable) this.changeCurrentDir(node);
    } else {
      this.state.tree.currentItem = node;
    }
    this.setState({});
  }

  onNodeToggledInNav = () => {
    this.setState({});
  }

  changeCurrentDir = (node) => {
    this.state.tree.setCurrentDir(node);
    this.props.history.push(node.meta.path);
  }
}

Explorer = withRouter(Explorer);

export default Explorer;
