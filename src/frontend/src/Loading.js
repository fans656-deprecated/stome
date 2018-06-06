import React from 'react';
import { ClipLoader as Spinner } from 'react-spinners';

export default class Loading extends React.Component {
  state = {showing: false}

  componentDidMount = async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    this.setState({showing: true});
  }

  render() {
    if (!this.props.loading) return null;
    return (
      <span style={{
          marginLeft: '.5em',
          position: 'relative',
          top: '.1em',
        }}
      >
        <Spinner loading={this.state.showing}
          size={8}
          color='var(--fg-color)'
        />
      </span>
    );
  }
}
