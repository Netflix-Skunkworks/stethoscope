import React, { Component } from 'react'
import { Link } from 'react-router'
import './App.css'
import Config from './Config.js'
import DataStore from './DataStore.js'

document.title = Config.appName

class App extends Component {

  constructor (props) {
    super(props)
    this.dismiss = this.dismiss.bind(this)
    this.store = new DataStore()
    this.state = {
      errors: []
    }
  }

  setEmail () {
    const email = this.props.email || decodeURIComponent(window.location.pathname.slice(1))
    if (process.env.NODE_ENV === 'development' && !email) window.location = '/user@example.com'
    this.setState({
      email: email
    })
  }

  showError (error, category) {
    this.setState({
      errors: [error]
    })
  }

  load (collectionName, loadFn) {
    const self = this
    const newState = {}
    loadFn(this.state.email).then(function (data) {
      newState[collectionName] = data
      self.setState(newState)
    }).catch(function (err) {
      const errMessage = `Error loading ${collectionName}`
      console.log(errMessage, err)
      self.showError(errMessage)
      newState[collectionName] = false
      self.setState(newState)
    })
  }

  componentDidUpdate (prevProps, prevState) {
    if (prevState.email !== this.state.email) {
      this.load('devices', this.store.loadDevices)
      this.load('accounts', this.store.loadAccounts)
      this.load('notifications', this.store.loadNotifications)
    }
  }

  componentDidMount () {
    this.setEmail()
  }

  dismiss (notification) {
    this.setState({
      notifications: this.state.notifications.filter(n => n._id !== notification._id)
    })
  }

  data () {
    return {
      email: this.state ? this.state.email : undefined,
      devices: this.state ? this.state.devices : undefined,
      accounts: this.state ? this.state.accounts : undefined,
      notifications: this.state ? this.state.notifications : undefined,
      dismiss: this.dismiss
    }
  }

  render () {
    const errors = (
      <div>{this.state.errors.map((e) => <div className='callout-danger panel message text-danger' key={e}>{e}</div>)}</div>
    )

    const show = function (name) {
      return Config.pages.includes(name.toLowerCase())
    }

    return (
      <div>
        <nav>
          <div className='main'>
            <a className='brand' href='#'>{Config.appName}</a>
            <ul>
              { show('overview') && <li><Link to='overview' activeClassName='active'>Overview</Link></li> }
              { show('devices') && <li><Link to='devices' activeClassName='active'>Devices</Link></li> }
              { show('accounts') && <li><Link to='accounts' activeClassName='active'>Accounts</Link></li> }
              { show('faq') && <li><Link to='faq' activeClassName='active'>FAQ</Link></li> }
            </ul>
          </div>
          <ul className='right'>
            <li>{this.state.email}</li>
          </ul>
        </nav>

        <main>
          {errors}

          {this.props.children && React.cloneElement(this.props.children, {
            store: this.data()
          })}

        </main>
      </div>
    )
  }
}

export default App
