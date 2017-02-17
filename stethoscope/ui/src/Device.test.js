/* eslint-env mocha */

import React from 'react'
import ReactDOM from 'react-dom'
import Device from './Device'

it('renders without crashing', () => {
  const div = document.createElement('div')
  ReactDOM.render(<Device />, div)
})
