import React, { Component } from 'react'
import './Notification.css'
import SimpleNotification from './notifications/Simple'
import Loader from './Loader'

const notificationComponents = [
  SimpleNotification
]

class Notification extends Component {

  constructor (opts) {
    super(opts)
    this.state = {
      dismissed: false,
      status: {}
    }
    this.dismiss = this.dismiss.bind(this)
    this.statusChange = this.statusChange.bind(this)
    this.notificationComponents = (this.props && this.props.notificationComponents) || notificationComponents
  }

  getNotificationComponent (data) {
    for (let i = 0; i < this.notificationComponents.length; i++) {
      const c = this.notificationComponents[i]
      if (c.handles(data)) return c
    }
  }

  dismiss () {
    this.setState({ dismissed: true })
    if (this.props.onDismiss) this.props.onDismiss(this.props.data)
  }

  statusChange (status) {
    this.setState({ status: status })
  }

  render () {
    if (this.state.dismissed) return null
    // get the proper notification Component for this alert
    const notificationComponent = this.getNotificationComponent(this.props.data)
    if (!notificationComponent) {
      console.log('No notification component found for notification', this.props.data, 'searched', this.notificationComponents)
      return null
    }
    const innerNotification = React.createElement(notificationComponent, { data: this.props.data, onDismiss: this.dismiss, onStatusChange: this.statusChange })
    let statusMessage = null
    if (this.state.status.state === 'saving') {
      statusMessage = this.state.status.message || <Loader />
    }
    if (this.state.status.state === 'error') {
      statusMessage = this.state.status.message || 'Error saving response'
    }
    let statusEl = null
    if (statusMessage) {
      statusEl = (
        <div className={`${this.state.status.state} notification-status`}>
          {statusMessage}
        </div>
      )
    }
    return (<div className='panel active notification'>
      {innerNotification}
      {statusEl}
    </div>)
  }
}

export default Notification
