/* eslint-env mocha */

import React from 'react'
import ReactDOM from 'react-dom'
import Action from './Action'

it('renders without crashing', () => {
  const div = document.createElement('div')
  const action = {
    title: 'Test action'
  }
  ReactDOM.render(<Action action={action} />, div)
})
