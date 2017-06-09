import React, { Component } from 'react'
import Spinner from './Spinner'
import { criticalOnly } from './utils/device-filter'
import Notification from './Notification'
import CriticalDeviceSummary from './CriticalDeviceSummary'

class Overview extends Component {
  constructor (opts) {
    super(opts)
    this.dismiss = this.dismiss.bind(this)
  }

  dismiss (notification) {
    this.props.store.dismiss(notification)
  }

  render () {
    if (!this.props.store) return null
    const notifications = this.props.store.notifications

    const criticalDevices = criticalOnly(this.props.store.devices)
    const criticalDevicesSummary = <CriticalDeviceSummary devices={criticalDevices} />

    if (notifications && this.props.store.devices !== undefined) {
      if (notifications.length > 0 || criticalDevicesSummary) {
        return <div className='narrow'>
          {criticalDevices.length > 0 && <div className='panel active notification'>
            <p>{criticalDevicesSummary}</p>
            <a className='nf-button btn btn-error' href='#/devices'>View devices</a>
          </div>}
          {notifications.map((n) => <Notification data={n} key={n._id || n.id || n.key} onDismiss={this.dismiss} />)}
        </div>
      } else {
        return (
          <div className='narrow'>
            <div className='panel'>
              You don&rsquo;t have any alerts. Now&rsquo;s a great time to <a href='#/devices/'>review your devices</a>.
            </div>
          </div>
        )
      }
    } else {
      return (
        <Spinner>Loading notifications...</Spinner>
      )
    }
  }
}

export default Overview
