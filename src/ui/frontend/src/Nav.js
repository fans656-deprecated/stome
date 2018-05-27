import React from 'react';
import IconDown from 'react-icons/lib/fa/angle-down';
import IconRight from 'react-icons/lib/fa/angle-right';
//import { ClipLoader as Spinner } from 'react-spinners';

import './css/Nav.css';

export default class Tree extends React.Component {
  render() {
    return (
      <div className="nav">
        <div className="tree">
          {this.renderNodes(this.props.tree.root, 0, 0)}
        </div>
      </div>
    );
  }

  renderNodes = (root, ith, depth) => {
    const nodes = [];
    let classes = ['tree-node'];
    if (root.isCurrentDir()) {
      classes.push('active');
    }
    nodes.push(
      <div className={classes.join(' ')}
        key={ith + '-' + depth}
        style={{paddingLeft: (depth * 1.3) + 'em'}}
        onClick={() => this.props.onNodeClicked(root)}
        onMouseDown={(ev) => ev.preventDefault()}
      >
        <Arrow node={root} onClick={(ev) => this.toggleNode(ev, root)}/>
        <Name node={root}/>
      </div>
    );
    if (root.toggled && root.dirs) {
      root.dirs.forEach((child, i) => {
        nodes.push(...this.renderNodes(child, i, depth + 1));
      });
    }
    return nodes;
  }

  toggleNode = async (ev, node) => {
    ev.stopPropagation();
    await node.toggle();
    this.props.onNodeToggled();
  }
}

const Arrow = ({node, onClick}) => {
  const Icon = node.toggled ? IconDown : IconRight;
  return (
    <Icon
      className="tree-node-arrow"
      size={20}
      style={{
        visibility: node.hasSubDirs() ? 'visible' : 'hidden',
      }}
      onClick={onClick}
    />
  );
}

const Name = ({node}) => {
  let name = node.meta.name;
  if (name.length === 0) name = '/';
  return (
    <a className="tree-node-name">
      {name}
    </a>
  );
}

//class Loading extends React.Component {
//  state = {loading: false}
//
//  componentDidMount = async () => {
//    await new Promise(resolve => setTimeout(resolve, 100));
//    this.setState({loading: true});
//  }
//
//  render() {
//    return (
//      <span style={{
//          marginLeft: '.5em',
//          position: 'relative',
//          top: '.2em',
//        }}
//      >
//        <Spinner loading={this.state.loading}
//          size={8}
//          color='var(--fg-color)'
//        />
//      </span>
//    );
//  }
//}
