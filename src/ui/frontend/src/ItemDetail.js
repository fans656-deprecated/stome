import React from 'react';

export default class Detail extends React.Component {
  render() {
    const item = this.props.item;
    let detail = [];
    detail = detail.concat([
      ['Name', item.name],
      ['Path', item.path],
      ['Owner', item.owner],
      ['Group', item.group],
      ['Access', accessToString(item.access)],
    ]);
    if (item.type === 'file') {
    }
    return (
      <div className="item-detail">
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
