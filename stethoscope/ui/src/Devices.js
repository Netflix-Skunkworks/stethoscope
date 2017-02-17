import React, { Component } from 'react'
import Device from './Device'
import Spinner from './Spinner'
import './Devices.css'

class Devices extends Component {

  render () {
    if (!this.props.store) return null

    const devices = this.props.store.devices
    const criticalDevices = devices ? devices.filter((d) => d.deviceRating === 'critical') : []

    let deviceSummary = null

    if (criticalDevices.length > 0) {
      const count = criticalDevices.length
      const pluralizedDevices = 'device' + (count !== 1 ? 's' : '')
      const pluralizedRequires = 'require' + (count === 1 ? 's' : '')
      const devicesList = criticalDevices.map(function (d) {
        return [d.manufacturer, d.model].join(' ')
      }).join(', ')

      deviceSummary = (
        <div className='panel callout callout-danger'>
          You have <span className='text-danger'>{count}</span> {pluralizedDevices} that {pluralizedRequires} attention:
          &nbsp;
          <span className='text-danger'>
            {devicesList}
          </span>
        </div>
      )
    }

    if (devices) {
      if (devices.length > 0) {
        return (
          <div>
            {deviceSummary}
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
