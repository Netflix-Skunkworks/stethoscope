import React, { Component } from 'react'
import './Spinner.css'

class Spinner extends Component {
  render () {
    return (
      <div className='loader-wrapper'>
        <div className='loader'>Loading...</div>
        <div className='loader-text'>{this.props.children}</div>
      </div>
    )
  }
}

export default Spinner
