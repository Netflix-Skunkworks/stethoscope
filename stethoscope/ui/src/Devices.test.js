/* eslint-env mocha */
/* global expect */

import React from 'react'
import { shallow } from 'enzyme'
import ReactDOM from 'react-dom'
import Devices from './Devices'
import Spinner from './Spinner'

it('renders without crashing', () => {
  const div = document.createElement('div')
  ReactDOM.render(<Devices />, div)
})

it("shows a loading message if devices haven't loaded", () => {
  const store = {
    email: 'test@example.com'
  }
  const el = shallow(<Devices store={store} />)
  const loading = <Spinner>Loading device data...</Spinner>
  expect(el.contains(loading)).toEqual(true)
})

it("doesn't show a loading message if devices are provided", () => {
  const store = {
    email: 'test@example.com',
    devices: [{}]
  }
  const el = shallow(<Devices store={store} />)
  const loading = <Spinner>Loading device data...</Spinner>
  expect(el.contains(loading)).toEqual(false)
})

it("doesn't show a loading message if device list is empty", () => {
  const store = {
    email: 'test@example.com',
    devices: []
  }
  const el = shallow(<Devices store={store} />)
  const loading = <div>Loading devices for {store.email}...</div>
  expect(el.contains(loading)).toEqual(false)
})

it("shows a 'no devices' warning if device list is empty", () => {
  const store = {
    email: 'test@example.com',
    devices: []
  }
  const el = shallow(<Devices store={store} />)
  const noDevices = <div className='panel'>No devices found for <strong>{store.email}</strong>.</div>
  expect(el.contains(noDevices)).toEqual(true)
})
