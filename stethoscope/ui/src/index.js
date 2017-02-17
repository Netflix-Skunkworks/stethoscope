import React from 'react'
import ReactDOM from 'react-dom'
import { Router, Route, IndexRedirect, hashHistory } from 'react-router'
import './screenplay.css'
import './nav.css'
import './index.css'
import './index-mobile.css'

import App from './App'
import Overview from './Overview'
import Devices from './Devices'
import Accounts from './Accounts'
import Faq from './Faq'

ReactDOM.render(
  <Router history={hashHistory}>
    <Route path='/' component={App}>
      <IndexRedirect to='overview' />
      <Route path='overview' component={Overview} />
      <Route path='devices' component={Devices} />
      <Route path='accounts' component={Accounts} />
      <Route path='faq' component={Faq} />
    </Route>
  </Router>,
  document.getElementById('root')
)
