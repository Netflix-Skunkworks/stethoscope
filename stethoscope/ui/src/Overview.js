import React, { Component } from 'react'
import Spinner from './Spinner'
import Notification from './Notification'

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

    if (notifications) {
      if (notifications.length > 0) {
        return <div className='narrow'>{notifications.map((n) => <Notification data={n} key={n._id || n.id || n.key} onDismiss={this.dismiss} />)}</div>
      } else {
        return (
          <div className='narrow'>
            <div className='panel'>
              You don&rsquo;t have any alerts. Now&rsquo;s a great time to <a href='#/devices/'>review your devices</a>.
            </div>
          </div>
        )
      }
    } else if (notifications === false) {
      return null
    } else {
      return (
        <Spinner>Loading notifications...</Spinner>
      )
    }
  }
}

export default Overview
