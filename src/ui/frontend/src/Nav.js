import React from 'react';
import { Treebeard } from 'react-treebeard';

import { getListDirectoryResults } from './util';

export default class Nav extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      cursor: null,
      root: [],
    };
  }

  componentWillReceiveProps(props) {
    const cursor = this.state.cursor;
    if (!cursor || cursor.dir.path !== props.activePath) {
      let node = getActiveNode(this.state.root, props.activePath);
      expand(node);
      this.onToggle(node, true);
      this.setState({
        cursor: node,
      });
    }
  }

  async componentDidMount() {
    const res = await getListDirectoryResults(this.props.path);
    this.populate(res.dirs);
  }

  populate = (dirs) => {
    const path = this.props.path;
    const root = {
      name: path,
      toggled: true,
      children: [],
      dir: {
        name: path,
        path: path,
      }
    };
    root.children = makeChildren(root, dirs);
    this.setState({root: root});
  }

  render() {
    return (
      <div className="nav">
        <Treebeard data={this.state.root} onToggle={this.onToggle}/>
      </div>
    );
  }

  onToggle = async (node, toggled) => {
    if (this.state.cursor) {
      this.state.cursor.active = false;
    }
    node.active = true;
    if (node.children) {
      node.toggled = toggled;
    }
    const res = await getListDirectoryResults(node.dir.path);
    node.loading = false;
    node.children = makeChildren(node, res.dirs);
    this.setState({
      cursor: node
    });
    this.props.onActivePathChanged(node.dir.path);
  }
}

function makeChildren(parent, dirs) {
  return dirs.map(dir => {
    return {
      name: dir.name,
      loading: true,
      children: [],
      dir: dir,
      parent: parent,
    };
  });
}

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
