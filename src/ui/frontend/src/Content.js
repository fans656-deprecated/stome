import React from 'react';

import Items from './Items';

export default class Content extends React.Component {
  render() {
    return (
      <div className="content"
        onClick={() => this.props.onClick(null)}
      >
        <Items
          dirs={this.props.dir.dirs}
          files={this.props.dir.files}
          onClick={this.props.onClick}
          onMouseDown={(ev) => ev.preventDefault()}
        />
      </div>
    );
  }
}
