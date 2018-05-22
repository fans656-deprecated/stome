import React from 'react';
import IconDown from 'react-icons/lib/fa/angle-down';
import IconRight from 'react-icons/lib/fa/angle-right';

import './css/Tree.css';

export default class Tree extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      root: props.tree,
      activeNode: null,
    };
  }

  componentWillReceiveProps(props) {
    this.setState({root: props.tree});
  }

  render() {
    console.log(this.state.root);
    return <div className="tree">{this.makeNodes(this.state.root, 0, 0)}</div>;
  }

  update = () => this.setState({})

  toggle = async (node, toggled) => {
    if (toggled === undefined) {
      toggled = !node.toggled;
    }
    if (node.loading) {
      node.children = await this.props.loadChildren(node);
      node.loading = false;
    }
    node.toggled = toggled;
    this.setState({});
  }

  expand = (node, update) => {
    node.toggled = true;
    if (update) this.update();
  }

  makeNodes = (root, depth, ith) => {
    const nodes = [];
    if (root.toggled === undefined) {
      root.toggled = false;
    }
    let Icon = null;
    Icon = root.toggled ? IconDown : IconRight;
    const classes = ['tree-node'];
    if (root.active && root === this.state.activeNode) {
      classes.push('active');
    }
    nodes.push(
      <div className={classes.join(' ')}
        key={ith + '-' + depth}
        style={{
          paddingLeft: depth + 'em',
        }}
        onClick={() => {
          root.active = true;
          if (root === this.state.activeNode) {
            root.toggled = !root.toggled;
          }
          this.setState({
            activeNode: root,
          });
        }}
          onMouseDown={ev => ev.preventDefault()}
      >
        <Icon
          className="tree-node-arrow"
          size={20}
          style={{
            visibility: root.hasChildren ? 'visible' : 'hidden',
          }}
          onClick={() => this.toggle(root)}
        />
        <span className="tree-node-name">
          {root.name}
        </span>
      </div>
    );
    if (root.toggled && root.children) {
      root.children.forEach((child, i) => {
        nodes.push(...this.makeNodes(child, depth + 1, i));
      });
    }
    return nodes;
  }
}
