import { Component } from 'react'
import { withRouter } from 'react-router'
import Config from './Config.js'
import ReactGA from 'react-ga'

if (Config.GATrackingId) {
  ReactGA.initialize(Config.GATrackingId)
}

function logPageView (location) {
  // remove userid from location string
  const locationString = (location.pathname + location.search + location.hash).replace(/\/\w+(%40|@)[^/]+/, '')
  ReactGA.set({ page: locationString })
  ReactGA.pageview(locationString)
}

class Tracker extends Component {
  componentDidMount () {
    logPageView(window.location)
  }
  componentDidUpdate (prevProps) {
    if (this.props.location && this.props.location.action !== 'POP') return
    if (this.props.location !== prevProps.location) {
      logPageView(window.location)
    }
  }
  render () {
    return null
  }
}

export default withRouter(Tracker)
