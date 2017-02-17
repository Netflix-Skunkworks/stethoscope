/* eslint-env mocha */

import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import Notification from './Notification'

class TestNotification extends Component {
  render () {
    return <div>{this.props.data.description}</div>
  }
}
TestNotification.handles = function (data) {
  return data.type && data.type === 'TestNotification'
}

it('renders without crashing', () => {
  const div = document.createElement('div')
  const data = {
    description: 'Generic alert for example user',
    type: 'TestNotification'
  }
  ReactDOM.render(<Notification notificationComponents={[TestNotification]} data={data} />, div)
})
