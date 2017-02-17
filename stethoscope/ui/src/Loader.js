import React, { Component } from 'react'
import './Loader.css'

class Loader extends Component {
  render () {
    return (
      <div className='small-loader'>
        <div className='bounce1' />
        <div className='bounce2' />
        <div className='bounce3' />
      </div>
    )
  }
}

export default Loader
