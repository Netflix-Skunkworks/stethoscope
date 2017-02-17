/* eslint-env mocha */

import React from 'react'
import ReactDOM from 'react-dom'
import Accounts from './Accounts'

it('renders without crashing', () => {
  const div = document.createElement('div')
  const store = { accounts: [] }
  ReactDOM.render(<Accounts store={store} />, div)
})
