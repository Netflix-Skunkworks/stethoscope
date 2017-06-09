import React, { Component } from 'react'
import Device from './Device'
import Spinner from './Spinner'
import CriticalDeviceSummary from './CriticalDeviceSummary'
import './Devices.css'

class Devices extends Component {

  render () {
    if (!this.props.store) return null
    const devices = this.props.store.devices
    if (devices) {
      if (devices.length > 0) {
        return (
          <div>
            <div className='panel callout callout-danger'>
              <CriticalDeviceSummary store={this.props.store} />
            </div>
            <div id='device-list'>
              { devices.map((d) => <Device device={d} key={JSON.stringify([d.identifiers, d.last_sync])} />)}
            </div>
          </div>
        )
      } else {
        return <div className='panel'>No devices found for <strong>{this.props.store.email}</strong>.</div>
      }
    } else if (devices === false) {
      return null
    } else {
      return (
        <Spinner>Loading device data...</Spinner>
      )
    }
  }
}

export default Devices
