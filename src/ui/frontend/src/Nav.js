import React from 'react';
import PropTypes from 'prop-types';

import Tree from './Tree';
import { fetchDir } from './util';

export default class Nav extends React.Component {
  state = {
    tree: null,
  }

  componentWillReceiveProps = async (props) => {
    //console.log(props);
    //await this.expandTo(props.activePath || props.rootPath);
  }

  componentDidMount = async () => {
    const rootPath = this.props.rootPath;
    const dir = await fetchDir(rootPath, 2);
    const root = makeNode(dir);
    root.loaded = true;
    root.toggled = true;
    const currentPath = this.props.currentPath || rootPath;
    const lastNode = await expand(root, currentPath);
    console.log(root);
    //this.setState({tree: root}, () => this.tree.select(lastNode));
  }

  render() {
    //console.log(this.props.currentPath);
    return null;
    if (!this.state.tree) return null;
    return (
      <div className="nav">
        <Tree
          ref={ref => this.tree = ref}
          root={this.state.tree}
          load={loadChildren}
          onSelect={this.setActiveDir}
        />
      </div>
    );
  }

  setActiveDir = (node) => {
    this.props.onActiveDirChanged(node.dir);
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
    loaded: false,
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

async function loadNode(node) {
  node.children = await loadChildren(node);
  node.loaded = true;
  return node;
}

async function loadChildren(node) {
  const dir = await fetchDir(node.dir.path, 2);
  return dir.dirs.map(makeNode);
}

function makeNode(dir) {
  const node = {
    name: dir.name,
    loaded: false,
    dir: dir,
  };
  if (dir.dirs) {
    node.children = dir.dirs.map(makeNode);
  }
  return node;
}

async function expand(root, path) {
  return await _expand(root, path.split('/'));
}

async function _expand(root, names) {
  if (names.length === 0 || root.name !== names[0]) return null;
  root.toggled = true;
  if (!root.loaded) await loadNode(root);
  names = names.splice(1);
  let ret = root;
  if (names.length > 0) {
    for (let child of root.children) {
      ret = await _expand(child, names) || ret;
    }
  }
  return ret;
}
