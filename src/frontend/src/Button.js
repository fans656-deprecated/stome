import React from 'react';
import IconQuestion from 'react-icons/lib/fa/question';

export class IconButton extends React.Component {
  render() {
    const Icon = this.props.icon || IconQuestion;
    return (
      <button
        className="icon"
        title={this.props.title}
        onClick={this.props.onClick}
      >
        <Icon size={18}/>
      </button>
    );
  }
}
