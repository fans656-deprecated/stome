import React from 'react'
import {KB, MB, GB, TB} from './constant'

export default class Detail extends React.Component {
  render() {
    const node = this.props.node;
    const meta = node.meta;
    let detail = [];
    const createdOnRemote = !node.transfer
      || node.transfer.status === 'uploading';
    if (createdOnRemote) {
      detail = detail.concat([
        ['Name', meta.name || '/'],
        ['Path', meta.path],
        ['Owner', meta.owner],
        ['Group', meta.group],
        ['Access', accessToString(meta.access)],
        ['Size', formatSize(meta.size)],
      ]);
      if (meta.type === 'file') {
      }
    } else {
      //
    }
    return (
      <div className="item-detail" style={{
        wordWrap: 'break-word',
      }}>
      {
        detail.map(([name, value]) => (
          <p key={name}><span>{name}</span>: <span>{value}</span></p>
        ))
      }
    </div>
    );
  }
}

function accessToString(access) {
  let a = [];
  a.push(access & 0o400 ? 'r' : '-');
  a.push(access & 0o200 ? 'w' : '-');
  a.push(access & 0o040 ? 'r' : '-');
  a.push(access & 0o020 ? 'w' : '-');
  a.push(access & 0o004 ? 'r' : '-');
  a.push(access & 0o002 ? 'w' : '-');
  return a.join('');
}

function formatSize(size) {
  if (size === 0) {
    return humanSize(size);
  } else {
    return humanSize(size) + ` (${size})`;
  }
}

function humanSize(size) {
  if (size === 0) {
    return '' + size;
  } else if (size < KB) {
    return size + 'B';
  } else if (size < MB) {
    return (size / KB).toFixed(0) + 'KB';
  } else if (size < GB) {
    return (size / MB).toFixed(0) + 'MB';
  } else if (size < TB) {
    return (size / GB).toFixed(0) + 'GB';
  } else {
    return (size / TB).toFixed(0) + 'TB';
  }
}
