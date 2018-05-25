import React from 'react';

import './css/Dialog.css';

export default class Dialog extends React.Component {
  state = {
    showing: true,
  }

  render() {
    if (!this.state.showing) return null;
    return (
      <div className="dialog" onClick={this.hide}>
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
    this.setState({showing: true});
  }

  hide = () => {
    this.setState({showing: false});
  }

  onContentClicked = (ev) => {
    ev.stopPropagation();
  }
}
