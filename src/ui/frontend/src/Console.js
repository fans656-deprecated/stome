import React from 'react';
import IconSearch from 'react-icons/lib/fa/search';
import IconUpload from 'react-icons/lib/fa/upload';
import IconCommand from 'react-icons/lib/fa/angle-right';
import './css/Console.css';

export default class Console extends React.Component {
  constructor(props) {
    super(props);
    this.types = [
      'search', 'upload',
    ];
    const iType = 0;
    this.state = {
      focus: false,
      text: '',
      iType: iType,
      type: this.types[iType],
    }
  }

  render() {
    const type = this.state.type;
    let Icon = IconSearch;
    if (type === 'upload') {
      Icon = IconUpload;
    } else if (type === 'command') {
      Icon = IconCommand;
    }
    return (
      <div className={'console' + (this.state.focus ? ' focus' : '')}>
        <Icon className="console-icon"/>
        <input
          onChange={this.onChange}
          onFocus={() => this.setState({focus: true})}
          onBlur={() => this.setState({focus: false})}
          onKeyPress={this.onKeyPress}
        />
      </div>
    );
  }

  onChange = ({target}) => {
    const text = target.value;
    this.setState({
      text: text,
    });
  }

  onKeyPress = (ev) => {
    if (ev.key === 'Enter') {
      this.handleEnter();
    } else if (ev.key === ' ') {
      if (this.state.text === '') {
        this.switchToNextType();
        ev.preventDefault();
      }
    }
  }

  handleEnter = () => {
    const type = this.state.type;
    const text = this.state.text.trim();
    if (type === 'search') {
      console.log(`Search: "${text}"`);
    } else if (type === 'upload') {
      console.log(`Upload: "${text}"`);
      window.upload(text);
    }
  }

  switchToNextType = () => {
    let iType = this.state.iType;
    iType = (iType + 1) % this.types.length;
    this.setState({
      iType: iType,
      type: this.types[iType],
    });
  }
}
