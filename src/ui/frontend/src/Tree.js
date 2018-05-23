import React from 'react';
import IconDown from 'react-icons/lib/fa/angle-down';
import IconRight from 'react-icons/lib/fa/angle-right';
import { ClipLoader as Spinner } from 'react-spinners';

import './css/Tree.css';

export default class Tree extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      root: props.root,
      activeNode: null,
    };
  }

  componentWillReceiveProps(props) {
    this.setState({root: props.root});
  }

  render() {
    return (
      <div className="tree">
        {this.makeNodes(this.state.root, 0, 0)}
      </div>
    );
  }

  select = (node) => {
    this.setState({
      activeNode: node,
    }, () => this.getSelectHandler()(node));
  }

  toggle = async (node, toggled, update) => {
    if (!node.loaded) {
      node.loading = true;
      this.update();
      node.children = await this.props.load(node);
      node.loaded = true;
      node.loading = false;
    }
    node.toggled = toggled == null ? !node.toggled : toggled;
    if (update == null || update) {
      this.update(() => this.getToggleHandler()(node));
    }
  }

  makeNodes = (root, ith, depth) => {
    const nodes = [];
    let classes = ['tree-node'];
    const active = root === this.state.activeNode;
    if (active) {
      classes.push('active');
    }
    nodes.push(
      <div className={classes.join(' ')}
        key={ith + '-' + depth}
        style={{paddingLeft: depth + 'em'}}
        onClick={() => this.onNodeClicked(root)}
        onMouseDown={(ev) => ev.preventDefault()}
      >
        <Arrow node={root} onClick={(ev) => this.onArrowClicked(ev, root)}/>
        <Name node={root}/>
        {root.loading && <Loading/>}
      </div>
    );
    if (root.toggled && root.children) {
      root.children.forEach((child, i) => {
        nodes.push(...this.makeNodes(child, i, depth + 1));
      });
    }
    return nodes;
  }

  onNodeClicked = (node) => {
    this.select(node);
    if (hasChildren(node) && node === this.state.activeNode) {
      this.toggle(node);
    }
  }

  onArrowClicked = (ev, node) => {
    ev.stopPropagation();
    this.select(node);
    this.toggle(node);
  }

  getClickHandler = () => this.props.onClick || (() => null)

  getToggleHandler = () => this.props.onToggle || (() => null)

  getSelectHandler = () => this.props.onSelect || (() => null)

  update = (callback) => this.setState({}, callback)
}

const Arrow = ({node, onClick}) => {
  const Icon = node.toggled ? IconDown : IconRight;
  return (
    <Icon
      className="tree-node-arrow"
      size={20}
      style={{
        visibility: hasChildren(node) ? 'visible' : 'hidden',
      }}
      onClick={onClick}
    />
  );
}

const Name = ({node}) => (
  <span className="tree-node-name">
    {node.name}
  </span>
);

class Loading extends React.Component {
  state = {loading: false}

  componentDidMount = async () => {
    await new Promise(resolve => setTimeout(resolve, 100));
    this.setState({loading: true});
  }

  render() {
    return (
      <span style={{
          marginLeft: '.5em',
          position: 'relative',
          top: '.2em',
        }}
      >
        <Spinner loading={this.state.loading}
          size={8}
          color='var(--fg-color)'
        />
      </span>
    );
  }
}

function hasChildren(node) {
  return node.children && node.children.length > 0;
}
