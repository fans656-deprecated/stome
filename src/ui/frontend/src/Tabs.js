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
    let tabs = this.props.children;
    if (!(tabs instanceof Array)) tabs = [tabs];
    const labelPosition = this.props.direction || 'top';
    let horz = true;
    if (labelPosition === 'left' || labelPosition === 'right') {
      horz = false;
    }
    const directionClass = horz ? 'horz' : 'vert';
    const labelsPosClass = labelPosition;
    const rootClasses = ['tabs', directionClass, labelsPosClass];
    const labelsClasses = ['tab-labels', directionClass, labelsPosClass];
    return (
      <div className={rootClasses.join(' ')}>
        <ul className={labelsClasses.join(' ')}>
          {
            tabs.map((tab, i) => (
              <TabLabel
                key={i}
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

  index = () => {
    return this.state.currentTabIndex;
  }

  onTabClicked = (index) => {
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
        {tab.props.name}
      </li>
    );
  }
}


