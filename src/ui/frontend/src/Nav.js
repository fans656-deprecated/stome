import React from 'react';
import PropTypes from 'prop-types';

import Tree from './Tree';
import { fetchDir } from './util';

export default class Nav extends React.Component {
  state = {
    tree: {},
  }

  componentWillReceiveProps = (props) => {
    //const cursor = this.state.cursor;
    //if (!cursor || cursor.dir.path != props.activePath) {
    //  this.expandToActivePath(props.activePath);
    //}
  }

  componentDidMount = async () => {
    const root = await fetchDir(this.props.rootPath);
    const tree = makeTree(root);
    tree.loading = false;
    tree.toggled = true;
    this.setState({tree: tree});
    //this.expandToActivePath(this.props.activePath);
    //this.tree.activate(this.props.activePath);
  }

  render() {
    return (
      <div className="nav">
        <Tree
          ref={ref => this.tree = ref}
          tree={this.state.tree}
          loadChildren={this.loadNodeChildren}
        />
      </div>
    );
  }

  loadNodeChildren = (node) => {
    console.log(node);
    return [];
  }

  expandToActivePath = async (path) => {
    let node = this.state.tree;
    const parts = path.split('/').splice(1);
    for (let part of parts) {
      await this.expand(node);
      if (node.children) {
        let found = false;
        for (let checkNode of node.children) {
          if (checkNode.dir.name === part) {
            node = checkNode;
            found = true;
            break;
          }
        }
        if (!found) {
          break;
        }
      }
    }
    this.onToggle(node, true);
  }

  expand = async (node) => {
    if (node.loading) {
      const dir = await fetchDir(node.dir.path);
      node.children = dir.dirs;
    }
    this.tree.expand(node, false);
  }

  setActiveDir = (node) => {
    this.props.onActiveDirChanged(node.dir);
    this.setState({
      cursor: node
    });
  }

  fetchNodeData = (node) => {
  }
}

Nav.propTypes = {
  rootPath: PropTypes.string,
  activePath: PropTypes.string,
};

function makeTree(root) {
  return {
    name: root.name,
    loading: true,
    hasChildren: root.children_count > 0,
    children: root.dirs ? root.dirs.map(makeTree) : [],
    dir: root,
  };
};

function getActiveNode(tree, path) {
  if (tree.dir.path === path) {
    return tree;
  }
  if (tree.children) {
    for (let child of tree.children) {
      let node = getActiveNode(child, path);
      if (node) {
        return node;
      }
    }
  }
}

function expand(node) {
  while (node.parent) {
    node = node.parent;
    node.toggled = true;
  }
}
