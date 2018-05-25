import React from 'react';

import './css/Edit.css';

export default class Edit extends React.Component {
  render() {
    const props = this.props;
    return (
      <div>
        <label className="edit-label">{props.name}</label>
        <input className="long" value={props.value}
          onChange={({target}) => props.onChange(target.value)}
        />
      </div>
    );
  }
}
