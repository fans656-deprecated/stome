import React from 'react';

import './css/Dialog.css';

export default class Dialog extends React.Component {
  state = {
    showing: false,
  }

  render() {
    if (!this.state.showing) return null;
    return (
      <div
        className="dialog"
        onClick={this.hide}
      >
        <div className="dialog-ui" onClick={this.onContentClicked}>
          <div className="dialog-content">
            {this.props.children}
          </div>
          {/*
          <div className="dialog-buttons">
            <button>Cancel</button>
            <button>OK</button>
          </div>
          */}
        </div>
        <div className="dialog-backdrop"/>
      </div>
    );
  }

  show = () => {
    this.eventid = window.on('keyup', this.onKeyUp);
    this.setState({showing: true});
  }

  hide = () => {
    window.off(this.eventid);
    this.setState({showing: false});
  }

  onKeyUp = (ev) => {
    if (ev.key === 'Escape') this.hide();
  }

  onContentClicked = (ev) => {
    ev.stopPropagation();
  }
}
