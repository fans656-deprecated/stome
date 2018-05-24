import React from 'react';

export default class Pather extends React.Component {
  render() {
    return (
      <div className="pather">
        <span>{false && this.props.path}</span>
      </div>
    );
  }
}
