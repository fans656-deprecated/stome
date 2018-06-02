import React from 'react';

import './css/Notification.css';

export function notifySuccess() {
}

export function notifyError() {
}

export default class Notification extends React.Component {
  state = {
    showing: false,
  }

  render() {
    if (!this.state.showing) return null;
    return (
      <div
        className="notification"
        onClick={this.destroy}
      >
        <p>hello world</p>
      </div>
    );
  }

  show = () => {
    this.eventid = window.on('keyup', this.onKeyUp);
    this.setState({showing: true});
  }

  destroy = () => {
    window.off(this.eventid);
    this.setState({showing: false});
  }

  onKeyUp = (ev) => {
    if (ev.key === 'Escape') this.destroy();
  }
}
