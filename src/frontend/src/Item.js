import React from 'react'

import conf from './conf'

import './css/Item.css'

import dirImg from './img/dir.png'
import fileImg from './img/file.png'

export default class Item extends React.Component {
  render() {
    const node = this.props.node;
    const meta = node.meta;

    let classes = ['item'];
    if (node.isCurrentItem()) {
      classes.push('active');
    }
    if (node.transfer || node.meta.status === 'init') {
      classes.push('transfer');
    }

    let icon = null;
    if (meta.listable) {
      icon = dirImg;
    } else {
      icon = fileImg;
    }

    let url = null;
    if (!node.transfer) {
      if (meta.listable) {
        url = meta.path;
      } else {
        url = conf.api_origin + meta.path;
      }
    }
    return (
      <div
        className={classes.join(' ')}
        onClick={this.onClick}
        onMouseDown={ev => ev.preventDefault()}
      >
        {
          node.transfer && <TransferThumbInfo node={node}/>
        }
        <div className="item-info">
          <img className="thumbnail" src={icon} alt={meta.path} width={64}/>
          <a
            className="name"
            href={url}
            onClick={ev => ev.preventDefault()}
          >
            {meta.name}
          </a>
        </div>
      </div>
    );
  }

  getItem = () => {
    return this.props.node;
  }

  onClick = (ev) => {
    this.props.onClick(this.props.node);
    ev.stopPropagation();
  }

  activate = () => {
    this.setState({active: true});
  }

  deactivate = () => {
    this.setState({active: false});
  }
}

class TransferThumbInfo extends React.Component {
  render() {
    const node = this.props.node;
    const transfer = node.transfer;
    if (transfer.status === 'hashing') {
      const hashPercent = node.transfer.hashProgress.toFixed(0);
      return (
        <div className="transfer-thumb-info">
          <div>
            <span>Hashing... </span>
          </div>
          <div>
            <span>{hashPercent}</span>
            <span>%</span>
          </div>
        </div>
      );
    } else if (transfer.status === 'uploading') {
      const percent = node.transfer.progress.toFixed(2);
      return (
        <div className="transfer-thumb-info">
          <div>
            <span>Uploading... </span>
          </div>
          <div>
            <span>{percent}</span>
            <span>%</span>
          </div>
        </div>
      );
    }
  }
}
