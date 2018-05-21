import React from 'react';

import './css/Tabs.css';

export class Tabs extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentTabIndex: 0,
    };
  }

  render() {
    const tabs = this.props.children;
    return (
      <div className="tabs">
        <ul className="tab-labels">
          {
            tabs.map((tab, i) => (
              <TabLabel
                tab={tab}
                index={i}
                active={i === this.state.currentTabIndex}
                onClick={() => this.onTabClicked(i)}
              />
            ))
          }
        </ul>
        <div className="tab-content">
          {this.props.children[this.state.currentTabIndex]}
        </div>
      </div>
    );
  }

  onTabClicked = (index) => {
    console.log(index);
    this.setState({currentTabIndex: index});
  }
}

export class Tab extends React.Component {
  render() {
    return (
      <div className="tab">
        {this.props.children}
      </div>
    );
  }
}

class TabLabel extends React.Component {
  render() {
    const tab = this.props.tab;
    let classes = ['tab-label'];
    if (this.props.active) {
      classes.push('active');
    }
    return (
      <li className={classes.join(' ')}
        onClick={this.props.onClick}
      >
        {tab.props.label}
      </li>
    );
  }
}


