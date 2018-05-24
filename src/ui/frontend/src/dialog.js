import React from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

import './css/dialog.css';

function showDialog(component) {
  console.log(component);
  return null;
  const anchor = $('<div id="dialog-anchor"/>');
  $('body').append(anchor)
  $('.explorer').addClass('dialog-present');
  ReactDOM.render((
    <Dialog>
      {component}
    </Dialog>
  ), anchor[0]);
}

export default class Dialog extends React.Component {
  render() {
    if (!this.state.showing
    return (
      <div className="dialog" onClick={this.hide}>
        <div className="dialog-ui" onClick={this.onContentClicked}>
          <div className="dialog-content">
            {this.props.children}
          </div>
          <div className="dialog-buttons">
            <button>Cancel</button>
            <button>OK</button>
          </div>
        </div>
      </div>
    );
  }

  show = () => {
    const anchor = $('<div id="dialog-anchor"/>');
    $('body').append(anchor)
    $('.explorer').addClass('dialog-present');
    //console.log(this.render());
    return;
    ReactDOM.render(this.render(), anchor[0]);
  }

  hide = () => {
    $('.explorer').removeClass('dialog-present');
    $('#dialog-anchor').remove();
  }

  onContentClicked = (ev) => {
    ev.stopPropagation();
  }
}
